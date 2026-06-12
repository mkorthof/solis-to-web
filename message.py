import config
import helper

import json
import glob

def today(payload):
    ''' Get info e.g. power and yield values from current message payload '''
    data = {
        'timestamp': None,
        'date': None,
        'time': None,
        'temp': None,
        'power': None,
        'state': None,
        'warning': None,
        'e_today': None,
        'e_yesterday': None,
        'e_month': None,
        'e_year': None,
        'e_total': None
    }
    try:
        notification = json.loads(payload)['NOTIFICATION'][config.INVERTER_ID]
        data['timestamp'] = helper.fmt_timestamp(notification['INVERTER_TIME'])
        data['date'] = data['timestamp'].strftime("%Y-%m-%d")
        data['time'] = data['timestamp'].strftime("%H:%M:%S")
        data['temp'] = notification['INVERTER_TEMP']/10
        data['power'] = notification['APPARENT_POWER']
        data['state'] = notification['CURRENT_STATE']
        data['warning'] = notification['WARNING_INFO_DATA']
        data['e_today'] = notification['E_TODAY']/10
        try:
            data['e_yesterday'] = [v['yield'] for k, v in previous('yesterday').items()][0]
        except IndexError:
            pass
        data['e_month'] = notification['E_MONTH']
        data['e_year'] = notification['E_YEAR']
        data['e_total'] = notification['E_TOTAL']
    except KeyError as e:
        print(f'ERROR: parsing JSON for "Today" - {e}')
    return(data)
    

def pattern(period):
    ''' Return glob pattern for period '''
    pattern = None
    if (period == 'today' or period == 'yesterday'):
        pattern = f'{helper.prefix_date(period)}_*'
    elif (period == 'this_month' or period == 'this_year'):
        pattern = f'{helper.prefix_date(period)}*';
    else:
        pattern = '*'   
    return pattern


def previous(period):
    ''' Get previous info values from multiple json files '''
    data = {}
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/{pattern(period)}-solis.json'), reverse=True):
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f_json:
                payload = f_json.read()
            try:
                notification = json.loads(payload)['NOTIFICATION'][config.INVERTER_ID]
                timestamp = helper.fmt_timestamp(notification['INVERTER_TIME'])
                if (period in ['week', 'month', 'year'] and not helper.is_days_ago(timestamp, period)):
                    continue                
                e_today = notification['E_TODAY']/10
                a_power = notification['APPARENT_POWER']
                f_date, f_time = fn.split('/')[-1].split('-')[0].split('_')
                data[timestamp] = {
                    'fn': 'json/' + fn.split('/')[-1],
                    'f_date': f_date,
                    'f_time': f_time,
                    'power': a_power,
                    'yield': e_today,
                    'payload': payload
                }
            except json.decoder.JSONDecodeError as e:
                print(f'ERROR: decoding JSON from file "{fn}" - "{e}"')
        except (KeyError, IndexError) as e:
            pass
    return(data)
