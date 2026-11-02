import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config
import helper
import message


class MessageModuleTests(unittest.TestCase):
    def test_plot_fields_includes_expected_keys(self):
        device = {
            "APPARENT_POWER": 2500,
            "E_TODAY": 5.5,
            "E_MONTH": 120,
            "E_YEAR": 800,
            "E_TOTAL": 1200,
        }

        result = message.inverter_plot_fields(device)

        self.assertEqual(result["APPARENT_POWER"], 2500)
        self.assertEqual(result["E_TODAY"], 5.5)
        self.assertIsNone(result.get("PAC"))
        self.assertEqual(result["E_TOTAL"], 1200)

    def test_inverter_ts_reads_inverter_time(self):
        payload = json.dumps({
            "NOTIFICATION": {
                config.INVERTER_ID: {"INVERTER_TIME": "2026-09-11 19:03:04"}
            }
        })

        self.assertEqual(message.inverter_timestamp(payload), "2026-09-11 19:03:04")

    def test_inverter_ts_returns_none_for_missing_structure(self):
        self.assertIsNone(message.inverter_timestamp(json.dumps({"OTHER": {}})))

    def test_last_extracts_values_from_payload(self):
        payload = json.dumps({
            "NOTIFICATION": {
                config.INVERTER_ID: {
                    "APPARENT_POWER": 2500,
                    "E_TODAY": 5.5,
                    "INVERTER_TIME": 1726134184
                }
            }
        })

        result = message.inverter_notification(payload)

        self.assertEqual(result["APPARENT_POWER"], 2500)
        self.assertEqual(result["E_TODAY"], 5.5)
        self.assertEqual(message.inverter_timestamp(payload), 1726134184)

    def test_read_file_reads_json_files_for_period(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = {
                "NOTIFICATION": {
                    config.INVERTER_ID: {
                        "APPARENT_POWER": 2500,
                        "E_TODAY": 5.5,
                        "INVERTER_TIME": 1726134184
                    }
                }
            }
            today_path = f"/{helper.fpath_today()}"
            period_dir = root / "json" / Path(*helper.fpath_today().split("/"))
            period_dir.mkdir(parents=True)
            fn = period_dir / "1726134184.json"
            fn.write_text(json.dumps(payload), encoding="utf-8")

            with mock.patch.object(config, "WEBDIR", str(root)):
                with mock.patch("message.helper.is_days_ago", return_value=True):
                    result = message.read_files(today_path, "today")

            self.assertTrue(result)
            self.assertEqual(next(iter(result.values()))["NOTIFICATION"][config.INVERTER_ID]["APPARENT_POWER"], 2500)

    def test_inverter_notification_rejects_flat_payload(self):
        payload = json.dumps({
            config.INVERTER_ID: {
                "APPARENT_POWER": 2500,
                "INVERTER_TIME": 1726134184,
            }
        })

        result = message.inverter_notification(payload)

        self.assertEqual(result, {})

    def test_inverter_timestamp_returns_none_for_flat_payload(self):
        payload = json.dumps({
            config.INVERTER_ID: {
                "APPARENT_POWER": 3000,
                "E_TODAY": 7.5,
                "INVERTER_TIME": 1726134184,
            }
        })

        self.assertIsNone(message.inverter_timestamp(payload))


if __name__ == "__main__":
    unittest.main()
