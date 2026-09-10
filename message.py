import config
import db
import helper

import json
import glob


def plot_fields(device):
    ''' Return plot fields,  '''
    data = {}
    fields = list(config.PLOTS) + ['E_MONTH', 'E_YEAR', 'E_TOTAL']
    for f in fields:
        data[f] = device[f] if device.get(f) else None
    return(data)


def inverter_ts(payload):
    ''' Get device timestamp from current message payload '''
    data = None
    try:
        payload = json.loads(payload)
        inverter = payload['NOTIFICATION'][config.INVERTER_ID]
        data = inverter['INVERTER_TIME']
    except IndexError:
        pass
    return(data)


def read_file(period):
    data = {}
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/{helper.fn_date(period)}*-solis.json'), reverse=True):
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f_json:
                f_content = f_json.read()
            try:
                timestamp = inverter_ts(f_content)
                if (period in ['week', 'month', 'year'] and not helper.is_days_ago(timestamp, period)):
                    continue
                payload = json.loads(f_content)
                inverter = payload['NOTIFICATION'][config.INVERTER_ID]
                datetime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                data[datetime] = plot_fields(inverter)
                data[datetime]['fn'] = 'json/' + fn.split('/')[-1]
                #data[timestamp]['json'] = f_content
            except (KeyError, IndexError) as e:
                pass
        except json.decoder.JSONDecodeError as e:
            print(f'ERROR: decoding JSON from file "{fn}" - "{e}"')
    return(data)


def query_db(period, plot_key):
    '''' Query database with specific json path and key in 'payload' column '''
    data = {}
    for timestamp, payload in db.query_json_path(f'{helper.db_date(period)}%', f'$.NOTIFICATION.{config.INVERTER_ID}', plot_key):
        timestamp = inverter_ts(payload)
        if (period in ['week', 'month', 'year'] and not helper.is_days_ago(timestamp, period)):
            continue
        datetime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f'DEBUG: write_period_data db datetime={datetime} period={period} db_date={helper.db_date(period)}%')
        data[datetime] = {plot_key: payload}
    return(data)


def _query_db_all(period):
    ''' Query database with json path in 'payload' column '''
    data = {}
    for timestamp, payload in db.query_json_path(f'{helper.db_date(period)}%', f'$.NOTIFICATION.{config.INVERTER_ID,}'):
        try:
            timestamp = inverter_ts(payload)
            if (period in ['week', 'month', 'year'] and not helper.is_days_ago(timestamp, period)):
                continue
            payload = json.loads(payload)
            datetime = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            inverter = payload['NOTIFICATION'][config.INVERTER_ID]
            data = plot_fields(inverter)
            data[datetime] = payload
            # TODO: db - handle json files?
            #data[datetime]['fn'] = ''
            #data[datetime]['json'] = payload
        except (KeyError, IndexError) as e:
            pass
    return(data)


def last(payload):
    ''' Get values like power and yield from current message payload '''
    data = {}
    try:
        timestamp = inverter_ts(payload)
        payload = json.loads(payload)
        inverter = payload['NOTIFICATION'][config.INVERTER_ID]
        data = plot_fields(inverter)
        data['timestamp'] = timestamp
        data['date'] = data['timestamp'].strftime("%Y-%m-%d")
        data['time'] = data['timestamp'].strftime("%H:%M:%S")
        data['payload'] = payload
        data['e_yesterday'] = None
        try:
            data['e_yesterday'] = [vals['E_TODAY'] for _, vals in history('yesterday', None).items()][0]
        except IndexError:
            pass
    except KeyError as e:
        print(f'ERROR: parsing JSON for "Today" - {e}')
    return(data)
    

def history(period, plot_key=None):
    ''' Get previously stored values from (multiple) json '''
    data = {}
    if config.STORE == 'database':
        print(f'DEBUG: message - history (db) period={period} db_date={helper.db_date(period)}%')
        data = query_db(period, plot_key)
    else:
        data = read_file(period)
    return(data)
