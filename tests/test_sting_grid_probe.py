from contextlib import contextmanager
from types import SimpleNamespace
import unittest

from tools import sting_grid_probe
from tools.apc_mini import grid_led, launchpad_event
from tools.launchpad_mini import decode_rgb_lighting


def rgb_frame(*entries):
    payload = [value for address, rgb in entries for value in (3, address, *rgb)]
    return [0xF0, 0x00, 0x20, 0x29, 0x02, 0x0D, 0x03, *payload, 0xF7]


class MappingTests(unittest.TestCase):
    def test_grid_preserves_orientation_and_release_encodings(self):
        for note, address in ((0, 11), (7, 18), (8, 21), (25, 42), (58, 83), (63, 88)):
            for status, value in ((144, 127), (128, 57), (144, 0)):
                with self.subTest(note=note, status=status, value=value):
                    self.assertEqual(launchpad_event([status, note, value]), (status, address, value))

    def test_edge_controls_translate_to_cc_with_zero_value_on_release(self):
        for note, address in ((64, 91), (71, 98), (82, 89), (89, 19)):
            with self.subTest(note=note):
                self.assertEqual(launchpad_event([144, note, 127]), (176, address, 127))
                self.assertEqual(launchpad_event([128, note, 127]), (176, address, 0))
                self.assertEqual(launchpad_event([144, note, 0]), (176, address, 0))

        for message in ([176, 48, 127], [144, 98, 127], [145, 58, 127], [248]):
            self.assertIsNone(launchpad_event(message))

    def test_rgb_palette_and_off(self):
        frame = rgb_frame((83, (90, 80, 0)), (61, (0, 80, 90)),
                          (11, (64, 0, 127)), (42, (0, 0, 0)))
        leds = [grid_led(address, rgb) for address, rgb in decode_rgb_lighting(frame).items()]
        self.assertEqual(leds, [(144, 58, 5), (144, 40, 1), (144, 0, 3), (144, 25, 0)])
        self.assertIsNone(grid_led(19, (0, 80, 90)))

    def test_malformed_frames_and_echoed_input_do_not_change_leds(self):
        complete = rgb_frame((83, (90, 80, 0)))
        malformed = complete[:-2] + [0xF7]
        mixed = complete[:-1] + [0, 82, 3, 0xF7]
        for data in ([], [144, 83, 127], [176, 19, 127], malformed, mixed):
            self.assertEqual(decode_rgb_lighting(data), {})


class FakeMidi:
    def __init__(self, events, send_error=None):
        self.events = events
        self.send_error = send_error
        self.callbacks = {}
        self.sent = {"sting-out": [], "apc-out": []}

    @contextmanager
    def open_output(self, name):
        def send(message):
            if self.send_error == (name, message):
                raise OSError("device disconnected")
            self.sent[name].append(message)

        yield SimpleNamespace(send=send)

    @contextmanager
    def open_input(self, name, callback):
        self.callbacks[name] = callback
        try:
            if name == "apc-in":
                for source, data in self.events:
                    self.callbacks[source](SimpleNamespace(bytes=lambda: data))
            yield
        finally:
            del self.callbacks[name]


class BridgeTests(unittest.TestCase):
    args = SimpleNamespace(apc_input="apc-in", apc_output="apc-out",
                           sting_input="sting-in", sting_output="sting-out",
                           seconds=0, trace=True)

    def test_bidirectional_run_keeps_independent_holds_and_clears_lights(self):
        frame = rgb_frame((83, (90, 80, 0)), (42, (0, 0, 0)))
        midi = FakeMidi([
            ("apc-in", [144, 58, 127]),
            ("apc-in", [144, 25, 127]),
            ("apc-in", [144, 89, 127]),
            ("apc-in", [128, 58, 57]),
            ("sting-in", [176, 19, 127]),
            ("sting-in", frame),
            ("sting-in", frame),
            ("sting-in", rgb_frame((83, (0, 0, 0)), (42, (70, 70, 70)))),
        ])
        events = []
        sting_grid_probe.run(midi, self.args, events.append, tuple)

        sent = [(144, 83, 127), (144, 42, 127), (176, 19, 127), (128, 83, 57)]
        self.assertEqual(midi.sent["sting-out"], sent + [(128, 42, 0), (176, 19, 0)])
        self.assertEqual(midi.sent["apc-out"], [(144, 58, 5), (144, 25, 0), (144, 58, 0),
                                              (144, 25, 5), (144, 25, 0)])
        self.assertEqual(events[-1]["recent_apc_to_sting"], sent)
        self.assertEqual(events[-1]["sting_rgb_frames"], 3)
        self.assertEqual(events[-1]["sting_to_apc_leds"], 4)

    def test_output_error_still_releases_held_notes_and_clears_leds(self):
        frame = rgb_frame((83, (90, 80, 0)), (42, (70, 70, 70)))
        midi = FakeMidi([("apc-in", [144, 58, 127]), ("sting-in", frame)],
                        send_error=("apc-out", (144, 25, 5)))
        with self.assertRaisesRegex(RuntimeError, "device disconnected"):
            sting_grid_probe.run(midi, self.args, lambda entry: None, tuple)

        self.assertEqual(midi.sent["sting-out"], [(144, 83, 127), (128, 83, 0)])
        self.assertEqual(midi.sent["apc-out"], [(144, 58, 5), (144, 58, 0), (144, 25, 0)])
