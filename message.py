import config
import db
import helper

import datetime
import json
import glob


''' Messages '''


def collector_notification(payload):
    ''' Get collector notification from paypload '''
    data = {}
    try:
        if payload:
            payload_obj = json.loads(payload) if isinstance(payload, str) else payload
            data = payload_obj['NOTIFICATION'][config.COLLECTOR_ID]
    except (IndexError, KeyError):
        pass
    return data


def inverter_notification(payload):
    ''' Get inverter notification from payload '''
    data = {}
    try:
        if payload:
            payload_obj = json.loads(payload) if isinstance(payload, str) else payload
            if payload_obj.get('NOTIFICATION'):
                data = payload_obj['NOTIFICATION'][config.INVERTER_ID] 
    except (IndexError, KeyError):
        pass
    return data


def inverter_timestamp(payload):
    ''' Get inverter timestamp from payload '''
    data = None
    try:
        if payload:
            payload_obj = json.loads(payload) if isinstance(payload, str) else payload
            if inverter_notification(payload_obj):
                data = inverter_notification(payload_obj)['INVERTER_TIME']
    except (IndexError, KeyError):
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
                # TODO: temp convert ts back to dt obj
                #dt = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                dt = helper.fmt_datetime(timestamp, True)
                if (period in ['week', 'month', 'year'] and not helper.is_days_ago(dt, period)):
                    continue
                payload = json.loads(f_content)
                inverter = payload['NOTIFICATION'][config.INVERTER_ID]
                #dt = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                data[dt] = plot_fields(inverter)
                data[dt]['fn'] = 'json/' + fn.split('/')[-1]
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
        dt = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f'DEBUG: write_period_data db datetime={datetime} period={period} db_date={helper.db_date(period)}%')
        data[dt] = {plot_key: payload}
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
            inverter = payload['NOTIFICATION'][config.INVERTER_ID]
            data = plot_fields(inverter)
            dt = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            data[dt] = payload
            # TODO: db - handle json files?
            #data[dt]['fn'] = ''
            #data[dt]['json'] = payload
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
        # TODO: temp convert ts back to dt obj
        dt = helper.fmt_datetime(timestamp, True)
        data['timestamp'] = dt
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
