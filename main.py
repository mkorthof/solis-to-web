import config
import helper
import web
import db
from message import inverter_ts as message_ts

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import sys
import os
import random


################################
''' Solis (MQTT) to Web Client '''
################################


def on_connect(client, userdata, connect_flags, reason_code, properties=None):
    print(f'{helper.fmt_date()} INFO: Connected with result code "{reason_code}", subscribing to "{config.TOPIC}"')
    client.subscribe(config.TOPIC)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f'INFO: Disconnected with reason code: {reason_code}')


def on_message(client, userdata, message):
    ''' Write payload from last message to json file, and create index.html '''
    payload = message.payload.decode()
    print(f'{helper.fmt_date()} INFO: Received {payload}')
    helper.webdirs()
    helper.write_data()
    # TODO: mkdirs for new fn format with path  e.g. ./y/m/d/<ts.json>
    #os.makedirs(f'{helper.fn_json()}', exist_ok=True)
    #print(f'DEBUG: on_message {helper._fpath_date('today')}/{message_ts(payload)}.json')
    #with open(f'{config.WEBDIR}/json/{helper.fpath_date('today')}/{message_ts(payload)}.json', 'w', encoding='utf-8', errors='ignore') as f_json:
    with open(f'{config.WEBDIR}/json/{helper.fn_now()}', 'w', encoding='utf-8', errors='ignore') as f_json:
        f_json.write(payload)
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f_index:
        f_index.write(web.index_html(payload))


def test(period):
    fn = f'{config.WEBDIR}/json/{helper.last_message(period)['pf']}-solis.json'
    # fn = f'export/20260708_180444-solis.json'
    print(f'TEST: using "{fn}"')
    with open(f'{fn}', 'r', encoding='utf-8', errors='ignore') as f_json:
        payload = f_json.read()
    # TODO: test new fn format with path
    #os.makedirs(helper._fpath_date('today'), exist_ok=True)
    print(f'TEST: fmt_timestamp message_ts {helper.fmt_timestamp(message_ts(payload))} offset {helper.fmt_timestamp(message_ts(payload), True)}')
    print(f'TEST: fmt_datetime message_ts {helper.fmt_datetime(message_ts(payload))} offset {helper.fmt_datetime(message_ts(payload), True)}')
    print(f'TEST: new - makedirs {helper._fpath_date('today')}')  
    print(f'TEST: new - fpath_date today "{config.WEBDIR}/json/{helper._fpath_date('today')}/{message_ts(payload)}.json"')
    print(f'TEST: new - fpath_date yesterday "{config.WEBDIR}/json/{helper._fpath_date('yesterday')}/{message_ts(payload)}.json"')
    print(helper.conv_fn())
    exit(0)
    helper.webdirs()
    helper.write_data()
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f_index:
        f_index.write(web.index_html(payload))
    #db.insert(helper.db_date('now'), payload)
    #db.insert(ts(payload), payload)


def main():
    # v1: client = mqtt.Client()
    client_id = f'solis-to-web-client-{random.randint(0, 1000)}'  # NOSONAR
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=client_id)
    if config.BROKER_USERNAME and config.BROKER_PW:
        client.username_pw_set(config.BROKER_USERNAME, config.BROKER_PW)
        #client.reconnect_delay_set(min_delay=1, max_delay=60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.BROKER_HOST, config.BROKER_PORT, 60)
    client.loop_forever()
    for item in dir(config):
        if not item.startswith("__") and os.environ.get(item):
            config.item = os.environ[item]


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
    helper.conv_fn()
    sys.exit(0)


if '-h' in sys.argv:
    print(f'./{sys.argv[0]} [---test|--createdb|--importdb|--help]')
    sys.exit(0)


if __name__ == "__main__":
    main()
