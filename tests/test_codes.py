import unittest

import codes


class CodeTests(unittest.TestCase):
    def test_get_status_known_code(self):
        self.assertEqual(codes.get_status(3), "3, Normal / Generating (MPPT mode)")

    def test_get_status_unknown_code_raises_index_error(self):
        with self.assertRaises(IndexError):
            codes.get_status(999)

    def test_get_error_known_code(self):
        expected = "Code 1015, ['NO-Grid', 'The inverter does not detect the utility grid']"
        self.assertEqual(codes.get_error(1015), expected)

    def test_get_error_invalid_hex_returns_original_value(self):
        self.assertEqual(codes.get_error("0x1015"), "0x1015")


if __name__ == "__main__":
    unittest.main()
