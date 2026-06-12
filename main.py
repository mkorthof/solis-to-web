import config
import helper
import web
import plot

from shlex import join
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import sys
import os


################################
''' Solis MQTT to Web Client '''
################################


def on_connect(client, userdata, connect_flags, reason_code, properties=None):
    print(f'{helper.fmt_date()} INFO: Connected with result code "{reason_code}", subscribing to "{config.TOPIC}"')
    client.subscribe(config.TOPIC)


def write_period_html():
    ''' Write message history and plot html files '''
    for period in ['today'] + config.SHOW_PERIODS +  config.LINK_PERIODS:
        with open(f'{config.WEBDIR}/messages_{period}.html', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(web.history_html(period))
        plot.plot(period)

def on_message(client, userdata, message):
    ''' Write payload from last message to json file, and create index.html '''
    if not os.path.isdir(f'{config.WEBDIR}'):
        os.mkdir(f'{config.WEBDIR}')            
    if not os.path.isdir(f'{config.WEBDIR}/json'):
        os.mkdir(f'{config.WEBDIR}/json')    
    payload = message.payload.decode()
    print(f'{helper.fmt_date()} INFO: Received {payload}')
    with open(f'{config.WEBDIR}/json/{helper.prefix_date('now')}-solis.json', 'w', encoding='utf-8', errors='ignore') as f_json:
        f_json.write(payload)
    write_period_html()
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f_index:
        f_index.write(web.index_html(payload))


def test(period):
    fn = f'{config.WEBDIR}/json/{helper.get_last_message(period)['pf']}-solis.json'
    print(f'TEST: using "{fn}"')
    with open(f'{fn}', 'r', encoding='utf-8', errors='ignore') as f_json:
        payload = f_json.read()
    write_period_html()
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f_index:
        f_index.write(web.index_html(payload))

def main():
    # v1: client = mqtt.Client()
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="solis-to-web-client2")
    if config.BROKER_USERNAME and config.BROKER_PW:
        client.username_pw_set(config.BROKER_USERNAME, config.BROKER_PW)
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

if __name__ == "__main__":
    main()
