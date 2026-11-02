import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config
import helper
import web


class WebModuleTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "NOTIFICATION": {
                config.INVERTER_ID: {
                    "APPARENT_POWER": 2500,
                    "DC_TOTALPOWER": 3000,
                    "E_TODAY": 55,
                    "E_MONTH": 120,
                    "E_YEAR": 800,
                    "E_TOTAL": 1200,
                    "INVERTER_TEMP": 250,
                    "CURRENT_STATE": 3,
                    "WARNING_INFO_DATA": None,
                    "INVERTER_TIME": 1726134184,
                }
            }
        }

    def test_plot_html_reads_plot_file_contents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plot_dir = root / "plot"
            plot_dir.mkdir()
            plot_file = plot_dir / "today_E_TODAY.html"
            plot_file.write_text("<div>Plot body</div>", encoding="utf-8")

            with mock.patch.object(config, "WEBDIR", str(root)):
                result = helper.plot_html("today", "E_TODAY")

            self.assertIn("Plot body", result)

    def test_head_and_footer_render_expected_html(self):
        head_html = web.head()
        footer_html = web.footer()

        self.assertIn("<title>", head_html)
        self.assertIn(config.TITLE, head_html)
        self.assertIn("static/simple.css", head_html)
        self.assertIn("Page generated on", footer_html)
        self.assertIn("https://mqtt.org", footer_html)
        self.assertIn("https://plotly.com/python", footer_html)

    def test_messages_table_renders_payload_summary(self):
        payload = {
            "2026-09-11 19:00:00": {
                "NOTIFICATION": {
                    config.INVERTER_ID: {
                        "E_TODAY": 55,
                        "DC_TOTALPOWER": 2000,
                    }
                },
                "fn": "json/2026/09/11/1234.json",
            }
        }

        with mock.patch.object(config, "STORE_FILES", False):
            html = web._message_table_rows(payload)

        self.assertIn("2026-09-11 19:00:00", html)
        self.assertIn("5.5", html)
        self.assertIn("2.0", html)
        self.assertIn("<td>", html)

    def test_index_html_includes_expected_status_and_plot_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plot_dir = root / "plot"
            plot_dir.mkdir()
            for period in ["today", "yesterday"]:
                for plot in config.INDEX_PLOT_TYPES:
                    (plot_dir / f"{period}_{plot}.html").write_text(f"<div>{period} {plot}</div>", encoding="utf-8")
                for plot in config.PLOT_TYPES:
                    (plot_dir / f"{period}_{plot}.html").write_text(f"<div>{period} {plot}</div>", encoding="utf-8")

            today_data = {
                "2026-09-11 19:00:00": {
                    "NOTIFICATION": {
                        config.INVERTER_ID: {"E_TODAY": 55, "DC_TOTALPOWER": 2000}
                    }
                }
            }
            yesterday_data = {
                "2026-09-10 18:00:00": {
                    "NOTIFICATION": {
                        config.INVERTER_ID: {"E_TODAY": 60, "DC_TOTALPOWER": 1800}
                    }
                },
                "2026-09-10 18:05:00": {
                    "NOTIFICATION": {
                        config.INVERTER_ID: {"E_TODAY": 65, "DC_TOTALPOWER": 1900}
                    }
                },
            }

            payload = json.dumps(self.payload)
            data = helper.set_index_values(payload, {"today": today_data, "yesterday": yesterday_data})

            with mock.patch.object(config, "WEBDIR", str(root)):
                html = web.index_html(data)

            self.assertIn("Status", html)
            self.assertIn("Last updated", html)
            self.assertIn("Energy Yield Today", html)
            self.assertIn("Messages", html)
            self.assertIn("Show All", html)
            self.assertIn("plot/", html)


if __name__ == "__main__":
    unittest.main()
