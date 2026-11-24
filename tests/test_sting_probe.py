from contextlib import nullcontext
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import sting_probe


class ProbeTests(unittest.TestCase):
    def test_gestures_send_press_and_release(self):
        for gesture, expected in (
            ("type-one", [[144, 81, 127], [128, 81, 0]]),
            ("generate", [[176, 19, 127], [176, 19, 0]]),
        ):
            with self.subTest(gesture=gesture):
                sent, records = [], []
                midi = SimpleNamespace(
                    Message=SimpleNamespace(
                        from_bytes=lambda data: SimpleNamespace(bytes=lambda: data)
                    ),
                    open_output=lambda port: nullcontext(
                        SimpleNamespace(send=lambda message: sent.append(message.bytes()))
                    ),
                )
                args = SimpleNamespace(action="send", port="test", gesture=gesture)
                with patch.object(sting_probe.time, "sleep"):
                    sting_probe.run(midi, args, records.append)
                self.assertEqual(sent, expected)
                self.assertEqual([record["bytes"] for record in records], expected)
                self.assertTrue(all(record["direction"] == "sent" for record in records))

    def test_capture_logs_sysex_without_an_output(self):
        def open_input(port, callback):
            callback(SimpleNamespace(bytes=lambda: [240, 0, 32, 41, 247]))
            return nullcontext()

        records = []
        with patch.object(sting_probe.time, "sleep"):
            sting_probe.run(SimpleNamespace(open_input=open_input),
                            SimpleNamespace(action="capture", port="test", seconds=1),
                            records.append)
        self.assertEqual(records[0]["direction"], "received")
        self.assertEqual(records[0]["bytes"], [240, 0, 32, 41, 247])
