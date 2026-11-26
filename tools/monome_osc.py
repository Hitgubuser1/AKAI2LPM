"""Local OSC transport for one virtual serialosc Grid 64."""

from struct import pack, unpack_from

LOOPBACK = "127.0.0.1"
DISCOVERY_PORT = 12002
DEVICE_ID = "m8192642"
DEVICE_TYPE = "monome 64"
SIZE = 8


def _string(value):
    data = value.encode("utf-8")
    return data + bytes(4 - len(data) % 4)


def encode(address, *args):
    tags = "," + "".join("s" if isinstance(value, str) else "i" for value in args)
    payload = (_string(value) if tag == "s" else pack(">i", value)
               for tag, value in zip(tags[1:], args))
    return _string(address) + _string(tags) + b"".join(payload)


def _read_string(packet, offset):
    end = packet.index(0, offset)
    next_offset = (end + 4) & ~3
    if next_offset > len(packet) or any(packet[end:next_offset]):
        raise ValueError("Invalid OSC string padding")
    return packet[offset:end].decode("utf-8"), next_offset


def decode(packet, depth=0):
    if packet.startswith(b"#bundle\0"):
        if len(packet) < 16 or depth == 4:
            raise ValueError("Invalid OSC bundle")
        messages = []
        offset = 16  # This bench applies LED feedback as it arrives.
        while offset < len(packet):
            if len(packet) - offset < 4:
                raise ValueError("Truncated OSC bundle")
            size, = unpack_from(">i", packet, offset)
            offset += 4
            if size <= 0 or size % 4 or offset + size > len(packet):
                raise ValueError("Invalid OSC bundle element size")
            messages.extend(decode(packet[offset:offset + size], depth + 1))
            offset += size
        return messages

    address, offset = _read_string(packet, 0)
    tags, offset = _read_string(packet, offset)
    if not address.startswith("/") or not tags.startswith(","):
        raise ValueError("Invalid OSC message header")
    args = []
    for tag in tags[1:]:
        if tag == "s":
            value, offset = _read_string(packet, offset)
        elif tag == "i" and len(packet) - offset >= 4:
            value, = unpack_from(">i", packet, offset)
            offset += 4
        else:
            raise ValueError("Unsupported or truncated OSC argument")
        args.append(value)
    if offset != len(packet):
        raise ValueError("Trailing OSC data")
    return [(address, tuple(args))]


def _reply_port(args):
    match args:
        case (int(port),) | ("localhost" | "127.0.0.1" | "::1", int(port)):
            if 0 < port < 65536:
                return port
    return None


class Grid:
    def __init__(self, send, device_port):
        self.send = send
        self.device_port = device_port
        self.target_port = None
        self.prefix = "/monome"

    def discovery(self, address, args):
        if address == "/serialosc/list" and len(args) == 2 and (port := _reply_port(args)):
            self.send(port, "/serialosc/device", DEVICE_ID, DEVICE_TYPE, self.device_port)
            return True
        return False

    def configure(self, address, args, source_port):
        match address, args:
            case "/sys/host", ("localhost" | "127.0.0.1" | "::1",):
                return True
            case "/sys/port", (int(port),) if _reply_port(args):
                self.target_port = port
                return True
            case "/sys/prefix", (str(prefix),) if prefix.startswith("/"):
                self.prefix = prefix.rstrip("/")
                return True
            case "/sys/rotation", (0,):
                return True
            case "/sys/info", _:
                port = _reply_port(args) if args else self.target_port or source_port
                if port is None:
                    return False
                self.send(port, "/sys/id", DEVICE_ID)
                self.send(port, "/sys/size", SIZE, SIZE)
                self.send(port, "/sys/host", LOOPBACK)
                self.send(port, "/sys/port", self.target_port or 0)
                self.send(port, "/sys/prefix", self.prefix)
                self.send(port, "/sys/rotation", 0)
                return True
        return False

    def key(self, x, y, pressed):
        if self.target_port is None:
            return False
        self.send(self.target_port, f"{self.prefix}/grid/key", x, y, int(pressed))
        return True

    def feedback(self, address, args):
        prefix = f"{self.prefix}/grid/led/"
        if not address.startswith(prefix) or not all(isinstance(value, int) for value in args):
            return ()
        command = address[len(prefix):]
        variable = command.startswith("level/")
        command = command.removeprefix("level/")
        limit = 15 if variable else 1

        def level(value):
            return value if variable else value * 15

        def line(values):
            if variable and len(values) == SIZE and all(0 <= value <= 15 for value in values):
                return values
            if not variable and len(values) == 1 and 0 <= values[0] <= 255:
                return tuple(15 * ((values[0] >> index) & 1) for index in range(SIZE))
            return ()

        match command, args:
            case "set", (x, y, value) if 0 <= x < SIZE and 0 <= y < SIZE and 0 <= value <= limit:
                return ((x, y, level(value)),)
            case "all", (value,) if 0 <= value <= limit:
                return tuple((x, y, level(value)) for y in range(SIZE) for x in range(SIZE))
            case "map", (0, 0, *values) if len(values) == (SIZE * SIZE if variable else SIZE):
                rows = [line(values[y * SIZE:(y + 1) * SIZE] if variable else values[y:y + 1])
                        for y in range(SIZE)]
                if all(rows):
                    return tuple((x, y, value) for y, row in enumerate(rows)
                                 for x, value in enumerate(row))
            case "row", (0, y, *values) if 0 <= y < SIZE:
                return tuple((x, y, value) for x, value in enumerate(line(values)))
            case "col", (x, 0, *values) if 0 <= x < SIZE:
                return tuple((x, y, value) for y, value in enumerate(line(values)))
        return ()
