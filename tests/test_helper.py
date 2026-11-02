import datetime
import unittest
from unittest import mock

import helper


class HelperTests(unittest.TestCase):
    def test_fmt_date_returns_datetime_string(self):
        fixed_now = datetime.datetime(2026, 9, 11, 19, 3, 4)

        with mock.patch.object(helper.datetime, "datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            self.assertEqual(helper.fmt_date_time(), "2026-09-11 19:03:04")

    def test_datetime_obj_uses_offset_when_requested(self):
        ts = 0
        value = helper.dt_obj(ts, offset=True)
        self.assertEqual(value, datetime.datetime.fromtimestamp(ts + 3600 * helper.config.TS_OFFSET))

    def test_fmt_timestamp_uses_offset_when_requested(self):
        ts = 0
        self.assertEqual(
            helper.fmt_timestamp(ts, offset=True),
            int(datetime.datetime.fromtimestamp(ts + 3600 * helper.config.TS_OFFSET).timestamp()),
        )

    def test_is_valid_filename_rejects_invalid_chars(self):
        self.assertTrue(helper.is_valid_filename("valid.txt"))
        self.assertFalse(helper.is_valid_filename("bad/name.txt"))
        self.assertFalse(helper.is_valid_filename("bad?.txt"))

    def test_mask_masks_serial_when_enabled(self):
        original = getattr(helper.config, "MASK", None)
        helper.config.MASK = True
        try:
            self.assertEqual(helper.mask("ABCDEF1234567890"), "ABCDEF******7890")
            self.assertEqual(
                helper.mask("prefixABCDEF1234567890suffix"),
                "prefixABCDEF******7890suffix",
            )
        finally:
            if original is None:
                delattr(helper.config, "MASK")
            else:
                helper.config.MASK = original

    def test_divide_handles_list_and_scalar_values(self):
        self.assertEqual(helper.divide(2000, 1000, 0), 2)
        self.assertEqual(helper.divide([2000, 4000], 1000, 1), 4)
        self.assertEqual(helper.divide({"value": 2000}, 1000, "value"), {"value": 2000})

    def test_is_days_ago_respects_period_boundaries(self):
        fixed_now = datetime.datetime(2026, 9, 11, 12, 0, 0)

        with mock.patch.object(helper.datetime, "datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            self.assertTrue(helper.is_days_ago(fixed_now, "today"))
            self.assertTrue(helper.is_days_ago(fixed_now - datetime.timedelta(days=1), "yesterday"))
            self.assertFalse(helper.is_days_ago(fixed_now - datetime.timedelta(days=2), "yesterday"))
            self.assertTrue(helper.is_days_ago(fixed_now - datetime.timedelta(days=7), "week"))
            self.assertFalse(helper.is_days_ago(fixed_now - datetime.timedelta(days=8), "week"))

    def test_mask_keeps_non_serial_text_unchanged(self):
        original = getattr(helper.config, "MASK", None)
        helper.config.MASK = True
        try:
            self.assertEqual(helper.mask("device-name"), "device-name")
            self.assertEqual(helper.mask("abc123"), "abc123")
        finally:
            if original is None:
                delattr(helper.config, "MASK")
            else:
                helper.config.MASK = original


if __name__ == "__main__":
    unittest.main()
