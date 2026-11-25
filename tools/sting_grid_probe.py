"""Run a bounded bidirectional APC mini MK1 and Sting bench session."""

import argparse
from collections import Counter, deque
from contextlib import ExitStack
import json
from threading import Event

from .apc_mini import CONTROL_CHANGE, NOTE_OFF, NOTE_ON, grid_led, launchpad_event
from .launchpad_mini import decode_rgb_lighting


def run(midi, args, emit, message_from_bytes):
    held = {}
    levels = {}
    counts = Counter()
    recent = deque(maxlen=128) if args.trace else None
    errors = []
    failed = Event()

    with midi.open_output(args.sting_output) as sting, midi.open_output(args.apc_output) as apc:
        def forward_input(message):
            if failed.is_set():
                return
            translated = launchpad_event(message.bytes())
            if translated is None:
                return

            status, address, value = translated
            key = (status == CONTROL_CHANGE, address)
            pressed = status != NOTE_OFF and value != 0
            if pressed:
                release_status = CONTROL_CHANGE if status == CONTROL_CHANGE else NOTE_OFF
                held[key] = (release_status, address, 0)

            try:
                sting.send(message_from_bytes(translated))
            except Exception as error:
                errors.append(error)
                failed.set()
                return

            if not pressed:
                held.pop(key, None)
            counts["apc_to_sting"] += 1
            if recent is not None:
                recent.append(translated)

        def forward_feedback(message):
            if failed.is_set():
                return
            entries = decode_rgb_lighting(message.bytes())
            if not entries:
                return

            counts["sting_rgb_frames"] += 1
            for address, rgb in entries.items():
                translated = grid_led(address, rgb)
                if translated is None:
                    continue
                _, note, value = translated
                if levels.get(note) == value:
                    continue

                try:
                    apc.send(message_from_bytes(translated))
                except Exception as error:
                    if value:
                        levels[note] = value
                    errors.append(error)
                    failed.set()
                    return

                levels[note] = value
                counts["sting_to_apc_leds"] += 1

        try:
            with ExitStack() as inputs:
                inputs.enter_context(midi.open_input(args.sting_input, callback=forward_feedback))
                inputs.enter_context(midi.open_input(args.apc_input, callback=forward_input))
                emit({"state": "listening", "seconds": args.seconds})
                failed.wait(args.seconds)
        except KeyboardInterrupt:
            pass
        finally:
            lights_off = ((NOTE_ON, note, 0) for note, value in levels.items() if value)
            for output, messages in ((sting, held.values()), (apc, lights_off)):
                for data in messages:
                    try:
                        output.send(message_from_bytes(data))
                    except Exception as error:
                        errors.append(error)

    if errors:
        raise RuntimeError(str(errors[0])) from errors[0]

    summary = {"state": "stopped", **counts}
    if recent is not None:
        summary["recent_apc_to_sting"] = list(recent)
    emit(summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apc_input")
    parser.add_argument("apc_output")
    parser.add_argument("sting_input", help="Port receiving feedback from Sting")
    parser.add_argument("sting_output", help="Port sending control messages to Sting")
    parser.add_argument("--seconds", type=int, default=120, choices=range(1, 301), metavar="1–300")
    parser.add_argument("--trace", action="store_true", help="Report the last 128 APC events after shutdown")
    args = parser.parse_args()

    try:
        import mido

        run(mido.Backend("mido.backends.rtmidi"), args,
            lambda entry: print(json.dumps(entry), flush=True), mido.Message.from_bytes)
    except (ImportError, OSError, RuntimeError) as error:
        parser.exit(1, f"Grid probe: {error}\n")


if __name__ == "__main__":
    main()
