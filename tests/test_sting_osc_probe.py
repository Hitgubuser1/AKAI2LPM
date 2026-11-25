from contextlib import contextmanager
from queue import Queue
import socket
from struct import pack
from threading import Thread
from types import SimpleNamespace
import unittest

from tools.monome_osc import DEVICE_ID, LOOPBACK, Grid, decode, encode
from tools.sting_osc_probe import apc_key, apc_led, run


class OscTests(unittest.TestCase):
    def test_wire_format_and_bundle_order(self):
        message = b"/sys/port\0\0\0,i\0\0\x00\x00\x2e\xe2"
        self.assertEqual(encode("/sys/port", 12002), message)
        config = encode("/sys/prefix", "/sting")
        bundle = b"#bundle\0" + pack(">Q", 1)
        bundle += pack(">i", len(message)) + message + pack(">i", len(config)) + config
        self.assertEqual(decode(bundle), [("/sys/port", (12002,)), ("/sys/prefix", ("/sting",))])
        for invalid in (message[:-1], message + b"\0", bundle[:-1], b"#bundle\0"):
            with self.subTest(packet=invalid), self.assertRaises(ValueError):
                decode(invalid)

    def test_led_commands_preserve_coordinates_and_zero(self):
        grid = Grid(lambda *_: None, 12003)
        lookup = lambda command, args: grid.feedback(f"/monome/grid/led/{command}", args)
        self.assertEqual(lookup("set", (7, 0, 1)), ((7, 0, 15),))
        self.assertEqual(lookup("level/set", (7, 0, 0)), ((7, 0, 0),))
        self.assertEqual(lookup("row", (0, 3, 129))[0::7], ((0, 3, 15), (7, 3, 15)))
        self.assertEqual(lookup("col", (3, 0, 1))[0::7], ((3, 0, 15), (3, 7, 0)))
        self.assertEqual(lookup("level/map", (0, 0, *range(8), *([0] * 56)))[7], (7, 0, 7))
        self.assertEqual(lookup("map", (0, 0, 0, 0, 0, 0, 0, 0, 0, 128))[-1], (7, 7, 15))
        self.assertEqual(lookup("level/row", (0, 2, *range(8)))[-1], (7, 2, 7))
        self.assertEqual(lookup("level/col", (2, 0, *range(8)))[-1], (2, 7, 7))
        self.assertEqual(len(lookup("all", (0,))), 64)
        self.assertEqual(lookup("level/map", (0, 0, *([0] * 63), 16)), ())

    def test_apc_mk1_grid_orientation_and_release(self):
        self.assertEqual(apc_key((144, 56, 127)), (0, 0, True))
        self.assertEqual(apc_key((128, 7, 127)), (7, 7, False))
        self.assertEqual(apc_key((144, 0, 0)), (0, 7, False))
        self.assertIsNone(apc_key((144, 89, 127)))

    def test_keyboard_distinguishes_normal_highlighted_and_off(self):
        self.assertEqual(apc_led(2, 7, 7, 1), (144, 2, 3))
        self.assertEqual(apc_led(2, 7, 15, 1), (144, 2, 5))
        self.assertEqual(apc_led(2, 7, 0, 1), (144, 2, 0))
        self.assertEqual(apc_led(7, 6, 7, 1), (144, 15, 3))
        self.assertEqual(apc_led(7, 6, 15, 1), (144, 15, 3))
        self.assertEqual(apc_led(7, 6, 0, 1), (144, 15, 0))
        self.assertEqual(apc_led(2, 2, 15, 1), (144, 42, 1))


class FakeApc:
    def __init__(self):
        self.leds = Queue()

    @contextmanager
    def open_output(self, _):
        yield SimpleNamespace(send=self.leds.put)

    @contextmanager
    def open_input(self, _, callback):
        self.callback = callback
        yield

    def key(self, status, note, velocity):
        self.callback(SimpleNamespace(bytes=lambda: (status, note, velocity)))


class LoopbackTests(unittest.TestCase):
    def test_full_round_trip_with_fake_sting_and_apc(self):
        apc = FakeApc()
        events = Queue()
        args = SimpleNamespace(apc_input="in", apc_output="out", seconds=1, min_level=1, trace=True)

        def probe():
            try:
                run(args, events.put, apc, tuple, discovery_port=0)
            except Exception as error:
                events.put({"error": error})

        worker = Thread(target=probe)
        worker.start()
        self.addCleanup(worker.join, 2)
        ready = events.get(timeout=2)
        self.assertEqual(ready.get("state"), "listening", ready)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sting:
            sting.bind((LOOPBACK, 0))
            sting.settimeout(1)

            def send(port, address, *values):
                sting.sendto(encode(address, *values), (LOOPBACK, port))

            def receive():
                packet, source = sting.recvfrom(1024)
                self.assertEqual(source, (LOOPBACK, ready["device_port"]))
                return decode(packet)[0]

            port = sting.getsockname()[1]
            send(ready["discovery_port"], "/serialosc/list", "localhost", port)
            path, info = receive()
            self.assertEqual((path, info), ("/serialosc/device", (DEVICE_ID, "monome 64", ready["device_port"])))
            device_port = info[2]
            send(device_port, "/sys/prefix", "/sting")
            send(device_port, "/sys/port", port)
            send(device_port, "/sys/info", "localhost", port)
            info = dict(receive() for _ in range(6))
            self.assertEqual(info["/sys/port"], (port,))
            self.assertEqual(info["/sys/prefix"], ("/sting",))
            self.assertEqual(info["/sys/size"], (8, 8))

            apc.key(144, 25, 127)
            apc.key(144, 0, 127)
            apc.key(144, 0, 0)
            self.assertEqual([receive() for _ in range(3)], [
                ("/sting/grid/key", (1, 4, 1)), ("/sting/grid/key", (0, 7, 1)),
                ("/sting/grid/key", (0, 7, 0)),
            ])
            send(device_port, "/sting/grid/led/level/set", 1, 4, 15)
            send(device_port, "/sting/grid/led/level/set", 1, 4, 0)
            send(device_port, "/sting/grid/led/set", 0, 0, 1)
            for value in (7, 15, 0):
                send(device_port, "/sting/grid/led/level/set", 2, 7, value)
            expected_leds = ((144, 25, 5), (144, 25, 0), (144, 56, 5),
                             (144, 2, 3), (144, 2, 5), (144, 2, 0))
            for expected in expected_leds:
                self.assertEqual(apc.leds.get(timeout=1), expected)

            summary = events.get(timeout=2)
            self.assertEqual(summary.get("state"), "stopped", summary)
            self.assertEqual(summary["apc_to_sting"], 3)
            self.assertEqual(summary["sting_to_apc_leds"], 6)
            self.assertEqual([frame[1][2] for frame in summary["keyboard_frames"]], [7, 15, 0])
            self.assertEqual(apc.leds.get_nowait(), (144, 56, 0))
            self.assertEqual(receive(), ("/sting/grid/key", (1, 4, 0)))
