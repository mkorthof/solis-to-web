import json
import unittest
from unittest import mock

import config
import main
import message


class RegressionTests(unittest.TestCase):
    @mock.patch("main.mqtt.Client")
    def test_main_starts_worker_and_connects(self, mock_client):
        with mock.patch.object(main.threading, "Thread") as mock_thread, \
             mock.patch.object(main.time, "sleep", side_effect=KeyboardInterrupt), \
             mock.patch.object(main.os.path, "isfile", return_value=True), \
             mock.patch.object(main.helper, "webdirs"), \
             mock.patch.object(main, "check_config", return_value=True):
            main.main()

        mock_thread.assert_called_once()
        mock_client.return_value.connect.assert_called_once()

    def test_inverter_ts_returns_none_for_missing_notification_block(self):
        payload = json.dumps({"OTHER": {}})

        self.assertIsNone(message.inverter_timestamp(payload))



if __name__ == "__main__":
    unittest.main()
