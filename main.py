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

import queue
import threading
import time


''' Solis (MQTT) to Web Client '''


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
            payload = message.payload.decode()
            print(f'{helper.fmt_date_time()} INFO: Worker received message payload (size={len(payload)})')
            helper.write_data(payload)
        except Exception as e:
            print(f'{helper.fmt_date_time()} ERROR: Worker processing message "{e}"')
        finally:
            # signal that the task is finished
            message_queue.task_done()


def check_config():
    # overwrite config if env var is set
    for item in dir(config):
        if not item.startswith("__") and os.environ.get(item):
            setattr(config, item, os.environ[item])
    try:
        config.BROKER_PASSWORD
        config.BROKER_USERNAME
        config.BROKER_HOST
        config.BROKER_PORT
        config.TOPIC
    except (NameError, TypeError, ValueError):
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
    payload = message.payload.decode()
    print(f'{helper.fmt_date_time()} INFO: Received payload (size={len(payload)}) {payload}')
    ts = inverter_timestamp(payload) if inverter_timestamp(payload) else helper.fmt_timestamp_now()
    helper.webdirs()
    if config.USE_FILES:
        os.makedirs(f'{config.WEBDIR}/json/{helper.fpath_today()}', exist_ok=True)
        with open(f'{config.WEBDIR}/json/{helper.fpath_today()}/{ts}.json', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(payload)
    if config.USE_DB:
        db.insert(ts, payload)
    helper.write_data(payload)


def test(period):
    # fn = f'{config.WEBDIR}/json/{helper.last_message(period)["pf"]}-solis.json'
    # fn = f'export/20260708_180444-solis.json'
    #print(f'{config.WEBDIR}/json/{helper.fn_date(period)}*/*.json')
    if period == 'today':
        print(f'TEST: fpath_today {helper.fpath_today()}')
        fn = max(sorted(glob.glob(f'{config.WEBDIR}/json/{helper.fpath_today()}/*.json', recursive=True)))
    elif period == 'yesterday':
        print(f'TEST: fpath_today {helper.fpath_yesterday()}')
        fn = max(sorted(glob.glob(f'{config.WEBDIR}/json/{helper.fpath_yesterday()}/*.json', recursive=True)))
    ts = None
    #print(f'TEST: using "{fn}"')
    with open(f'{fn}', 'r', encoding='utf-8', errors='ignore') as f:
        payload = f.read()
        ts = inverter_timestamp(payload) if inverter_timestamp(payload) else helper.fmt_timestamp_now()
    print(f'TEST: ts={helper.fmt_timestamp(ts)} offset={helper.fmt_timestamp(ts, True)} dt_obj="{helper.dt_obj(ts)}" offset="{helper.dt_obj(ts, True)}"')
    #print(f'TEST: makedirs {config.WEBDIR}/json/{helper.fpath_today()}')
    config.HEADER = (f'<pre style=font-size:0.5em>TEST: "{fn}"</pre>') + ''.join(config.HEADER)
    helper.webdirs()
    helper.write_data(payload)


def main():
    # start the processing worker in a background thread
    worker_thread = threading.Thread(target=message_worker, daemon=True)
    worker_thread.start()
    if not check_config():
        print('ERROR: invalid broker and/or topic setting')
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
    client.connect(config.BROKER_HOST, int(config.BROKER_PORT), 60)
    # reconnect options already handled for loop_forever 
    # using loop_start instead of loop_forever
    #   client.reconnect_delay_set(min_delay=1, max_delay=60)
    #   client.loop_forever(retry_first_connection=True)
    # start the non-blocking background network loop
    client.loop_start()
    try:
        # keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDisconnecting and exiting cleanly...")
        client.loop_stop()
        client.disconnect()    


if '--test' in sys.argv:
    try:
        period = sys.argv[2]
    except IndexError:
        period = 'today'
    test(period)
    sys.exit(0)


if '--createdb' in sys.argv:
    db.create_table()
    sys.exit(0)


if '--importdb' in sys.argv:
    db.import_json()
    sys.exit(0)


if '--convertfn' in sys.argv:
    apply = False
    if '--apply' in sys.argv:
        apply = True
    helper.conv_fn(apply)
    sys.exit(0)


if '-h' in sys.argv or '--help' in sys.argv:
    print(f'./{sys.argv[0]} [---test|--createdb|--importdb|--help]')
    sys.exit(0)

if __name__ == "__main__":
    main()
