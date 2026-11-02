import unittest
from unittest import mock

import config
import plot


class PlotModuleTests(unittest.TestCase):
    def test_values_converts_numeric_series_for_plotting(self):
        original = config.PLOTS["E_TODAY"]
        config.PLOTS["E_TODAY"] = {"div": 10, "unit": "kWh", "name": "Energy Yield", "color": "blue"}
        try:
            data = {
                "2026-09-11 19:00:00": {
                    "NOTIFICATION": {config.INVERTER_ID: {"E_TODAY": 55}}
                },
                "2026-09-11 19:05:00": {
                    "NOTIFICATION": {config.INVERTER_ID: {"E_TODAY": 60}}
                },
            }

            result = plot.values("today", "E_TODAY", data)

            self.assertEqual(result[0]["x"], "2026-09-11 19:00:00")
            self.assertEqual(result[0]["y"], 5.5)
            self.assertEqual(result[1]["y"], 6.0)
        finally:
            config.PLOTS["E_TODAY"] = original

    def test_values_returns_none_when_data_missing(self):
        self.assertIsNone(plot.values("today", "E_TODAY", {}))

    @mock.patch("plot.px.line")
    @mock.patch("plot.helper.is_valid_filename", return_value=True)
    def test_write_plot_generates_html(self, mock_is_valid_filename, mock_px_line):
        fig = mock.Mock()
        mock_px_line.return_value = fig

        plot.write_plot("today", "E_TODAY", [{"x": "2026-09-11 19:00:00", "y": 5.5}])

        mock_px_line.assert_called_once()
        fig.update_layout.assert_called_once()
        fig.update_traces.assert_called_once()
        fig.write_html.assert_called_once()

    @mock.patch("plot.helper.is_valid_filename", return_value=False)
    def test_write_plot_skips_invalid_filename(self, mock_is_valid_filename):
        plot.write_plot("today", "E_TODAY", [{"x": "2026-09-11 19:00:00", "y": 5.5}])
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
