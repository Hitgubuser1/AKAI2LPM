"""Run a bounded Sting Monome Grid 64 probe over local OSC."""

import argparse
from collections import Counter, deque
from contextlib import ExitStack
import json
import selectors
import socket
from threading import Lock
from time import monotonic, monotonic_ns

from .apc_mini import GREEN, NOTE_OFF, NOTE_ON, OFF, RED, YELLOW
from .monome_osc import DISCOVERY_PORT, LOOPBACK, SIZE, Grid, decode, encode


def apc_key(data):
    if len(data) != 3:
        return None
    status, note, velocity = data
    if status not in (NOTE_ON, NOTE_OFF) or not 0 <= note < SIZE * SIZE:
        return None
    row, column = divmod(note, SIZE)
    return column, SIZE - 1 - row, status == NOTE_ON and velocity > 0


def apc_led(x, y, level, minimum):
    colours = (YELLOW, GREEN, YELLOW, RED)
    colour = colours[y // 2]
    # The two rightmost pads in the lower rows are grid controls, not note keys.
    if y >= SIZE - 2 and x < SIZE - 1 and level == 15:
        colour = YELLOW
    return NOTE_ON, (SIZE - 1 - y) * SIZE + x, colour if level >= minimum else OFF


def bind_udp(stack, port):
    listener = stack.enter_context(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        listener.bind((LOOPBACK, port))
    except OSError as error:
        raise OSError(f"Cannot bind OSC UDP {LOOPBACK}:{port}: {error}") from error
    return listener


def run(args, emit, midi=None, message_from_bytes=None, discovery_port=DISCOVERY_PORT):
    counts = Counter()
    recent = deque(maxlen=48) if args.trace else None
    keyboard_frames = deque(maxlen=24) if args.trace else None
    watch_events = deque(maxlen=1024)
    watched = None
    watched_note = None
    if args.watch_pad is not None:
        row, column = args.watch_pad
        watched = column - 1, row - 1
        watched_note = (SIZE - row) * SIZE + column - 1
    start_ns = monotonic_ns()
    last_levels = [[0] * SIZE for _ in range(SIZE)]
    levels = {}
    held = set()
    lock = Lock()
    errors = []

    with ExitStack() as sockets:
        discovery = bind_udp(sockets, discovery_port)
        device = bind_udp(sockets, 0)
        selector = sockets.enter_context(selectors.DefaultSelector())
        selector.register(discovery, selectors.EVENT_READ)
        selector.register(device, selectors.EVENT_READ)

        def send(sock, port, address, *values):
            sock.sendto(encode(address, *values), (LOOPBACK, port))

        grid = Grid(lambda port, address, *values: send(device, port, address, *values),
                    device.getsockname()[1])

        def forward_input(message):
            event = apc_key(message.bytes())
            if event is None:
                return
            x, y, pressed = event
            with lock:
                if errors:
                    return
                try:
                    if grid.key(x, y, pressed):
                        if pressed:
                            held.add((x, y))
                        else:
                            held.discard((x, y))
                        counts["apc_to_sting"] += 1
                        if recent is not None:
                            recent.append(("key", x, y, int(pressed)))
                except OSError as error:
                    errors.append(error)

        with ExitStack() as outputs:
            apc = outputs.enter_context(midi.open_output(args.apc_output)) if midi else None
            try:
                with ExitStack() as inputs:
                    if midi:
                        inputs.enter_context(midi.open_input(args.apc_input, callback=forward_input))
                    emit({"state": "listening", "discovery_port": discovery.getsockname()[1],
                          "device_port": grid.device_port, "seconds": args.seconds})
                    deadline = monotonic() + args.seconds
                    while (remaining := deadline - monotonic()) > 0:
                        with lock:
                            if errors:
                                raise errors[0]
                        for selected, _ in selector.select(min(remaining, 0.25)):
                            sock = selected.fileobj
                            try:
                                packet, source = sock.recvfrom(65535)
                                received_at = monotonic_ns() if watched is not None else None
                                messages = decode(packet)
                            except ConnectionResetError:
                                continue
                            except ValueError:
                                counts["invalid_osc_packets"] += 1
                                continue
                            for address, values in messages:
                                with lock:
                                    if recent is not None and "/grid/led/" not in address:
                                        recent.append(("receive", address, values))
                                    if sock is discovery:
                                        if grid.discovery(address, values):
                                            counts["discovery_replies"] += 1
                                        continue
                                    if grid.configure(address, values, source[1]):
                                        counts["configuration_messages"] += 1
                                        continue
                                    feedback = grid.feedback(address, values)
                                if feedback:
                                    counts["sting_led_messages"] += 1
                                keyboard_changed = False
                                for x, y, level in feedback:
                                    is_watched = watched is not None and watched == (x, y)
                                    if last_levels[y][x] != level:
                                        if keyboard_frames is not None and y >= SIZE - 2:
                                            keyboard_changed = True
                                        if is_watched:
                                            watch_events.append((received_at - start_ns, "osc", level))
                                    last_levels[y][x] = level
                                    if apc is None:
                                        continue
                                    data = apc_led(x, y, level, args.min_level)
                                    _, note, colour = data
                                    if levels.get(note, OFF) != colour:
                                        levels[note] = colour
                                        apc.send(message_from_bytes(data))
                                        if is_watched:
                                            watch_events.append((monotonic_ns() - start_ns, "midi", colour))
                                        counts["sting_to_apc_leds"] += 1
                                if keyboard_changed:
                                    keyboard_frames.append(tuple(tuple(row) for row in last_levels[-2:]))
            except KeyboardInterrupt:
                pass
            finally:
                for x, y in held:
                    try:
                        grid.key(x, y, False)
                    except OSError as error:
                        errors.append(error)
                for note, colour in levels.items():
                    if colour:
                        try:
                            apc.send(message_from_bytes((NOTE_ON, note, OFF)))
                            if note == watched_note:
                                watch_events.append((monotonic_ns() - start_ns, "cleanup_midi", OFF))
                        except (OSError, RuntimeError) as error:
                            errors.append(error)

    if errors:
        raise RuntimeError(str(errors[0])) from errors[0]
    summary = {"state": "stopped", **counts}
    if recent is not None:
        summary.update(recent=list(recent), last_levels=last_levels, keyboard_frames=list(keyboard_frames))
    if watched is not None:
        summary.update(watch_pad=args.watch_pad, watch_events_ns=list(watch_events))
    emit(summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apc_input", nargs="?", help="APC MK1 input; omit both ports for discovery only")
    parser.add_argument("apc_output", nargs="?", help="APC MK1 output")
    parser.add_argument("--seconds", type=int, default=120, choices=range(1, 301), metavar="1–300")
    parser.add_argument("--min-level", type=int, default=1, choices=range(1, 16), metavar="1–15")
    parser.add_argument("--trace", action="store_true", help="Report recent OSC and raw LED levels on exit")
    parser.add_argument("--watch-pad", nargs=2, type=int, choices=range(1, SIZE + 1), metavar=("ROW", "PAD"),
                        help="Report timestamped OSC brightness and APC LED changes for one pad on exit")
    args = parser.parse_args()
    if bool(args.apc_input) != bool(args.apc_output):
        parser.error("specify both APC ports or neither")

    emit = lambda entry: print(json.dumps(entry), flush=True)
    try:
        if args.apc_input:
            import mido

            run(args, emit, mido.Backend("mido.backends.rtmidi"), mido.Message.from_bytes)
        else:
            run(args, emit)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f"OSC probe: {error}\n")


if __name__ == "__main__":
    main()
