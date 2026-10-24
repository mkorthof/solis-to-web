import config
import helper
import web
import db
from message import inverter_timestamp

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import sys
import os
import random
import glob


''' Solis (MQTT) to Web Client '''


def on_connect(client, userdata, connect_flags, reason_code, properties=None):
    print(f'{helper.fmt_date_time()} INFO: Connected with result code "{reason_code}", subscribing to "{config.TOPIC}"')
    client.subscribe(config.TOPIC)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f'INFO: Disconnected with reason code: {reason_code}')


def on_message(client, userdata, message):
    ''' Write payload from last message to json file, and create index.html '''
    payload = message.payload.decode()
    print(f'{helper.fmt_date_time()} INFO: Received {payload}')
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
    # overwrite config if env var is set
    for item in dir(config):
        if not item.startswith("__") and os.environ.get(item):
            setattr(config, item, os.environ[item])
    # v1: client = mqtt.sClient()
    client_id = f'solis-to-web-client-{random.randint(0, 1000)}'  # NOSONAR
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=client_id)
    if config.BROKER_USERNAME and config.BROKER_PASSWORD:
        client.username_pw_set(config.BROKER_USERNAME, config.BROKER_PASSWORD)
        #client.reconnect_delay_set(min_delay=1, max_delay=60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.BROKER_HOST, config.BROKER_PORT, 60)
    client.loop_forever()


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
