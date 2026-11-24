import unittest

from tools.apc_type_probe import translate


class TypePadTests(unittest.TestCase):
    def test_apc_to_sting(self):
        self.assertEqual(translate("pad", [144, 58, 127]), [144, 83, 127])
        self.assertEqual(translate("pad", [128, 58, 127]), [128, 83, 127])
        self.assertIsNone(translate("pad", [144, 57, 127]))

    def test_sting_to_apc(self):
        header = [240, 0, 32, 41, 2, 13, 3]
        for rgb, expected in (([90, 80, 0], 5), ([0, 0, 0], 0)):
            frame = header + [3, 82, 90, 80, 0, 3, 83] + rgb + [247]
            self.assertEqual(translate("led", frame), [144, 58, expected])
        self.assertIsNone(translate("led", [144, 83, 127]))
        self.assertIsNone(translate("led", header + [3, 83, 90, 247]))
