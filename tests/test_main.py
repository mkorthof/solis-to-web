import json
import os
import unittest
from unittest import mock

import config
import main


class MainModuleTests(unittest.TestCase):
    def test_on_connect_subscribes_to_configured_topic(self):
        client = mock.Mock()

        main.on_connect(client, None, None, 0)

        client.subscribe.assert_called_once_with(config.TOPIC)

    def test_on_disconnect_logs_reason_code(self):
        client = mock.Mock()

        with mock.patch("builtins.print") as mock_print:
            main.on_disconnect(client, None, None, 7, None)

        mock_print.assert_called_once()
        self.assertIn("7", mock_print.call_args[0][0])

    def test_on_message_enqueues_message_for_worker(self):
        payload = json.dumps({
            "NOTIFICATION": {
                config.INVERTER_ID: {
                    "APPARENT_POWER": 2500,
                    "E_TODAY": 5.5,
                    "INVERTER_TIME": 1726134184,
                }
            }
        })
        message_obj = mock.Mock()
        message_obj.payload.decode.return_value = payload
        message_obj.topic = "/test/topic"
        message_obj.mid = 42

        with mock.patch.object(main, "inverter_timestamp", return_value=1726134184), \
             mock.patch.object(main.helper, "webdirs") as mock_webdirs, \
             mock.patch.object(main.db, "insert") as mock_insert, \
             mock.patch.object(main.os, "makedirs") as mock_makedirs, \
             mock.patch.object(main.message_queue, "put") as mock_queue_put, \
             mock.patch("builtins.open", mock.mock_open()) as mock_open:
            main.on_message(mock.Mock(), None, message_obj)

        mock_webdirs.assert_called_once()
        mock_makedirs.assert_called_once_with(f"{config.WEBDIR}/json/{main.helper.fpath_today()}", exist_ok=True)
        mock_insert.assert_called_once_with(1726134184, payload)
        mock_queue_put.assert_called_once_with(message_obj)
        mock_open.assert_any_call(f"{config.WEBDIR}/json/{main.helper.fpath_today()}/{1726134184}.json", "w", encoding="utf-8", errors="ignore")
        mock_open.assert_any_call(f"{config.WEBDIR}/index.html", "w", encoding="utf-8", errors="ignore")

    def test_message_worker_processes_queued_message(self):
        payload = '{"a": 1}'
        message_obj = mock.Mock()
        message_obj.payload = payload.encode("utf-8")
        message_obj.mid = 99

        with mock.patch.object(main.helper, "write_data") as mock_write_data, \
             mock.patch.object(main.message_queue, "get", side_effect=[message_obj, KeyboardInterrupt]), \
             mock.patch.object(main.message_queue, "task_done") as mock_task_done:
            with self.assertRaises(KeyboardInterrupt):
                main.message_worker()

        mock_write_data.assert_called_once_with(payload)
        mock_task_done.assert_called_once()

    def test_main_applies_environment_overrides_without_exiting(self):
        original = {
            "BROKER_HOST": config.BROKER_HOST,
            "BROKER_PORT": config.BROKER_PORT,
            "TOPIC": config.TOPIC,
            "BROKER_USERNAME": config.BROKER_USERNAME,
            "BROKER_PASSWORD": config.BROKER_PASSWORD,
        }
        mock_client = mock.Mock()

        try:
            with mock.patch.dict(
                "os.environ",
                {"BROKER_HOST": "env-broker", "BROKER_PORT": "8883", "TOPIC": "/env/topic"},
                clear=False,
            ):
                with mock.patch.object(main.threading, "Thread") as mock_thread, \
                     mock.patch.object(main.time, "sleep", side_effect=KeyboardInterrupt), \
                     mock.patch.object(main.os.path, "isfile", return_value=True), \
                     mock.patch.object(main.helper, "webdirs"), \
                     mock.patch.object(main.mqtt, "Client", return_value=mock_client):
                    main.main()

            self.assertEqual(config.BROKER_HOST, "env-broker")
            self.assertEqual(config.BROKER_PORT, "8883")
            self.assertEqual(config.TOPIC, "/env/topic")
            mock_thread.assert_called_once()
            mock_client.connect.assert_called_once_with("env-broker", 8883, 60)
        finally:
            config.BROKER_HOST = original["BROKER_HOST"]
            config.BROKER_PORT = original["BROKER_PORT"]
            config.TOPIC = original["TOPIC"]
            config.BROKER_USERNAME = original["BROKER_USERNAME"]
            config.BROKER_PASSWORD = original["BROKER_PASSWORD"]


if __name__ == "__main__":
    unittest.main()
