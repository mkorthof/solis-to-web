import config
import helper
import web
import db
from message import inverter_timestamp
from message import read_files

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import sys
import os
import random
import glob
import json

import queue
import threading
import time


''' Solis 2 Web '''
''' Gets data using MQTT Client and creates html files '''


EXPECTED_CONFIG = {
    "BROKER_HOST": str,
    "BROKER_PORT": int,
    "BROKER_USERNAME": str,
    "BROKER_PASSWORD": str,
    "TOPIC": str,
    "INVERTER_ID": str,
    "COLLECTOR_ID": str,
    "TS_OFFSET": int,
    "STORE_FILES": bool,
    "USE_DATABASE": bool,
    "FN_DB": str,
    "WEBDIR": str,
    "JSONDIR": str,
    "PLOTDIR": str,
    "TITLE": str,
    "HEADER": str,
    "PERIODS": list,
    "PLOT_TYPES": list,
    "INDEX_PLOT_TYPES": list,
    "WEBSTATIC": bool,
    "WEBSTATIC_FILES": list,
    "PLOTS": dict,
    "DEBUG": bool,
    "DEBUG_LEVEL": int,
}

message_queue = queue.Queue()


def message_worker():
    ''' Worker thread that gets messages from queue and processes them '''
    print(f'{helper.fmt_date_time()} INFO: Worker thread started. Awaiting messages...')
    while True:
        try:
            # block=True and timeout=1 allows the loop to periodically check 
            # for exit conditions if needed, while remaining highly efficient
            message = message_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue
        # time consuming operations
        try:
            payload = message.payload.decode('utf-8')
            print(f'{helper.fmt_date_time()} INFO: Worker received message payload (size={len(payload)})')
            helper.write_data(payload)
        except Exception as e:
            print(f'{helper.fmt_date_time()} ERROR: Worker processing message "{e}"')
        finally:
            # signal that the task is finished
            message_queue.task_done()


def load_env_overrides() -> bool:
    """ Overwrites config attributes from environment variables, if set """
    for key, expected_type in EXPECTED_CONFIG.items():
        env_val = os.environ.get(key)
        if env_val is not None:
            try:
                if expected_type is bool:
                    normalized = env_val.strip().lower()
                    if normalized in {"true", "1"}:
                        setattr(config, key, True)
                    elif normalized in {"false", "1",}:
                        setattr(config, key, False)
                    else:
                        raise ValueError
                else:
                    setattr(config, key, expected_type(env_val))
            except ValueError:
                print(f'Could not set env var {key}={env_val}')
                return False
    return True


def is_valid_config() -> bool:
    """ Validates that config attributes exist and match expected types """
    if not load_env_overrides():
        return False
    for key, expected_type in EXPECTED_CONFIG.items():
        val = getattr(config, key, None)
        if not isinstance(val, expected_type):
            print(f'Unexpected setting {key}={val}')
            return False
        if expected_type is str and not val.strip():
            print(f'Unexpected setting ({key}={val}')
            return False
    return True


def on_connect(client, userdata, connect_flags, reason_code, properties=None):
    reason = f'"{reason_code.name}" ({reason_code})' if hasattr(reason_code, 'name') else f'"{reason_code}"'
    if reason_code == 0:
        print(f'{helper.fmt_date_time()} INFO: Connected with result {reason}, subscribing to "{config.TOPIC}"')
        client.subscribe(config.TOPIC)
    else:
        print(f'{helper.fmt_date_time()} INFO: Failed to connect {reason}')


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    reason = f'"{reason_code.name}" ({reason_code})' if hasattr(reason_code, 'name') else f'"{reason_code}"'
    print(f'{helper.fmt_date_time()} INFO: Disconnected with reason: {reason}')


def on_message(client, userdata, message):
    ''' Write payload from last message to json file, and create index.html '''
    # handle short-running tasks here (store json, create index.html
    # send longer running tasks to worker (plots, message viewer)
    payload = message.payload.decode('utf-8')
    try:
        json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print(f'ERROR: decoding JSON - "{e}"')
        return
    print(f'{helper.fmt_date_time()} INFO: Received payload (size={len(payload)}) {payload}')
    ts = inverter_timestamp(payload) if inverter_timestamp(payload) else helper.fmt_timestamp_now()
    helper.webdirs()
    if config.STORE_FILES:
        os.makedirs(f'{config.WEBDIR}/{config.JSONDIR}/{helper.fpath_today()}', exist_ok=True)
        with open(f'{config.WEBDIR}/{config.JSONDIR}/{helper.fpath_today()}/{ts}.json', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(payload)
    if config.USE_DATABASE:
        db.insert(ts, payload)
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(web.index_html(helper.set_index_values(payload, {})))
    message_queue.put(message)
    print(f'{helper.fmt_date_time()} INFO: Enqueued message from topic: "{message.topic}"\n')


def test(period):
    if not is_valid_config():
        print('ERROR: invalid config, exiting...')
        sys.exit(1)
    # fn = f'{config.WEBDIR}/{config.JSONDIR}/{helper.last_message(period)["pf"]}-solis.json'
    # fn = f'export/20260708_180444-solis.json'
    if period == 'today':
        #print(f'{config.WEBDIR}/{config.JSONDIR}/{helper.fn_date(period)}*/*.json')
        #{helper.fpath_today()}')
        #print(f'TEST: glob {config.WEBDIR}/{config.JSONDIR}/{helper.fpath_today()}/*.json')
        try:
            fn = max(sorted(glob.glob(f'{config.WEBDIR}/{config.JSONDIR}/{helper.fpath_today()}/*.json', recursive=True), reverse=True))
        except ValueError as e:
            print("TEST: error (try '--yesterday' ?), exiting...", e)
            sys.exit(1)
    elif period == 'yesterday':
        try:
            print(f'TEST: fpath_yesterday {helper.fpath_yesterday()}')
            fn = max(sorted(glob.glob(f'{config.WEBDIR}/{config.JSONDIR}/{helper.fpath_yesterday()}/*.json', recursive=True)))
        except ValueError as e:
            print('TEST: error, exiting...', e)
            sys.exit(1)
    ts = None
    print(f'TEST: using "{fn}"')
    with open(f'{fn}', 'r', encoding='utf-8', errors='ignore') as f:
        payload = f.read()
    try:
        ts = inverter_timestamp(payload)
    except Exception as e:
        print(f'TEST: unable to get INVERTER_TIME from json, using "now" instead (ts={ts})', e)
        ts = helper.fmt_timestamp_now()
    #print('TEST: payload =', payload)
    #print(f'TEST: makedirs {config.WEBDIR}/{config.JSONDIR}/{helper.fpath_today()}')
    config.HEADER = (f'<pre style=font-size:0.5em>TEST: "{fn}"</pre>') + ''.join(config.HEADER)
    helper.webdirs()
    helper.write_data(payload)


def main():
    # start the processing worker in a background thread
    worker_thread = threading.Thread(target=message_worker, daemon=True)
    worker_thread.start()
    if not is_valid_config():
        print('ERROR: invalid config, exiting...')
        sys.exit(1)
    if not os.path.isfile(config.FN_DB):
        db.create_table()
    helper.webdirs()
    # Initialize the MQTT Client with API Version 2 (Required for Paho 2.x+)
    # Use v1: client = mqtt.sClient()
    client_id = f'solis-to-web-client-{random.randint(0, 1000)}'  # NOSONAR
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=client_id)
    if config.BROKER_USERNAME and config.BROKER_PASSWORD:
        client.username_pw_set(config.BROKER_USERNAME, config.BROKER_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    for attempt in range(3):
        try:
            client.connect(config.BROKER_HOST, int(config.BROKER_PORT), 60)
            client.loop_start()
            break
        except Exception as e:
            print(f'{helper.fmt_date_time()} WARNING: Failed to connect {attempt + 1} times - {e}')
            time.sleep(2)
    else:
        print(f'{helper.fmt_date_time()} ERROR: startup failed after max retries, exiting...')
        sys.exit(1)
    # reconnect options already handled by loop_forever
    # using loop_start instead of loop_forever:
    #   client.reconnect_delay_set(min_delay=1, max_delay=60)
    #   client.loop_forever(retry_first_connection=True)
    # start the non-blocking background network loop
    try:
        # keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting and exiting cleanly...")
        client.loop_stop()
        client.disconnect()    


# handle arguments


if '--test' in sys.argv:
    try:
        period = sys.argv[2]
    except IndexError:
        period = 'today'
    test(period)
    sys.exit(0)


if '--create-db' in sys.argv:
    db.create_table()
    sys.exit(0)


if '--import-db' in sys.argv:
    replace = False
    fpath = '**'
    offset = True
    if '--no-offset' in sys.argv:
        offset=False
    if '--replace' in sys.argv:
        replace = True
    if len(sys.argv) > 1 and sys.argv[2]:
        fpath = sys.argv[2]
    for dt, payload in read_files(fpath).items():
        ts = helper.fmt_timestamp(dt.timestamp(), offset)
        #ts = ts-3600*7*2
        #print(offset, dt, ts, ts-3600*7, config.TS_OFFSET)
        # TODO: fix json conversion
        if replace:
            db.replace(ts, str(payload).replace("'", '"'))
        else:
            db.insert(ts, str(payload).replace("'", '"'))
    sys.exit(0)


if '--delete-db' in sys.argv:
    apply = False
    offset = True
    num_records = 0
    if '--apply' in sys.argv:
        apply = True
    if '--no-offset' in sys.argv:
        offset=False
    try:
        fpath = sys.argv[2]
    except IndexError:
        print('ERROR: need path to json, exiting...')
        sys.exit(1)
    for dt_obj in read_files(fpath).keys():
        # dry-run
        ts = helper.fmt_timestamp(dt_obj.timestamp(), offset)
        # ts = ts-3600*7
        result = db.query_ts(ts)
        if result:
            print(f'INFO: delete db dt={dt_obj} ts={ts} offset={offset} match records = {result}')
            num_records = num_records+1
        # actually delete
        if apply:
            #db.delete_ts(dt_obj.timestamp())
            ts = helper.fmt_timestamp(dt_obj.timestamp(), offset=offset)
            db.delete_ts(ts)
    if apply:
        print(f'INFO: Deleted {num_records} records.')
    else:
        print(f'INFO: Rerun with "--apply" to actually delete {num_records} records.')
    sys.exit(0)


if '--convert-files' in sys.argv:
    apply = False
    if '--apply' in sys.argv:
        apply = True
    helper.conv_fn(apply)
    if not apply:
        print('\nINFO: convert dry-run mode, rerun with "--apply" to actually move files')
    sys.exit(0)


if '-h' in sys.argv or '--help' in sys.argv:
    print(f'USAGE: ./{sys.argv[0]} [--test|--create-db|--import-db|--convert-files|]')
    sys.exit(0)

if __name__ == "__main__":
    main()
