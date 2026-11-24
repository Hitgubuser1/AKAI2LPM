"""Send Launchpad test gestures and capture replies as JSON Lines."""
import argparse
import json
import time

GESTURES = {
    "type-one": ([0x90, 81, 127], [0x80, 81, 0]),
    "type-two": ([0x90, 82, 127], [0x80, 82, 0]),
    "generate": ([0xB0, 19, 127], [0xB0, 19, 0]),
}


def event(direction, message):
    return {"time_ns": time.monotonic_ns(), "direction": direction,
            "bytes": list(message.bytes())}


def run(midi, args, emit, message_from_bytes=None):
    if args.action == "ports":
        emit({"inputs": midi.get_input_names(), "outputs": midi.get_output_names()})
        return
    if args.action == "capture":
        with midi.open_input(args.port, callback=lambda msg: emit(event("received", msg))):
            time.sleep(args.seconds)
        return
    with midi.open_output(args.port) as output:
        press, release = (message_from_bytes(data) for data in GESTURES[args.gesture])
        output.send(press)
        try:
            emit(event("sent", press))
            time.sleep(0.08)
        finally:
            output.send(release)
            emit(event("sent", release))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("ports")
    capture = commands.add_parser("capture")
    capture.add_argument("port")
    capture.add_argument("--seconds", type=int, default=60, choices=range(1, 301),
                         metavar="1–300")
    send = commands.add_parser("send")
    send.add_argument("port")
    send.add_argument("gesture", choices=GESTURES)
    args = parser.parse_args()
    try:
        import mido
        run(mido.Backend("mido.backends.rtmidi"), args,
            lambda entry: print(json.dumps(entry), flush=True), mido.Message.from_bytes)
    except (ImportError, OSError, RuntimeError) as error:
        parser.exit(1, f"MIDI probe: {error}\n")


if __name__ == "__main__":
    main()
