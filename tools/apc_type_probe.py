"""Bridge the third top-row Type pad in one direction for a bounded bench run."""
import argparse
import time


def translate(direction, data):
    if direction == "pad":
        if len(data) == 3 and data[0] in (128, 144) and data[1] == 58:
            return [data[0], 83, data[2]]
        return None

    if data[:7] != [240, 0, 32, 41, 2, 13, 3] or data[-1] != 247:
        return None
    entries = data[7:-1]
    if len(entries) % 5 or any(kind != 3 for kind in entries[::5]):
        return None
    for i in range(0, len(entries), 5):
        if entries[i + 1] == 83:
            return [144, 58, 5 if any(entries[i + 2:i + 5]) else 0]
    return None


def main():
    import mido

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=["pad", "led"])
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    with mido.open_output(args.destination) as output:
        held = False

        def forward(message):
            nonlocal held
            result = translate(args.direction, message.bytes())
            if result is not None:
                output.send(mido.Message.from_bytes(result))
                held = result[0] == 144 and result[2] > 0
                print("forwarded", bytes(result).hex(" "), flush=True)

        try:
            with mido.open_input(args.source, callback=forward):
                print("Listening for 60 seconds", flush=True)
                time.sleep(60)
        finally:
            if held:
                cleanup = [128, 83, 0] if args.direction == "pad" else [144, 58, 0]
                output.send(mido.Message.from_bytes(cleanup))


if __name__ == "__main__":
    main()
