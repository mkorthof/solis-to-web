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
    return data


def inverter_plot_fields(inverter_notification):
   ''' Return fields for plots '''
   data = {}
   for field in list(config.PLOTS) + ['E_MONTH', 'E_YEAR', 'E_TOTAL']:
       data[field] = inverter_notification[field] if inverter_notification.get(field) else None
   return data


def fpath_pattern(period):
    ''' Return date pattern for file glob '''
    if period == 'today': return helper.fpath_today()
    elif period == 'yesterday': return helper.fpath_yesterday()
    elif period == 'this_month': return f'{datetime.datetime.now().strftime("%Y/%m")}/*'
    elif period == 'this_year': return f'{datetime.datetime.now().strftime("%Y")}/*/*'
    return '**'


def dt_pattern(period):
    ''' Return datetime pattern used in db query '''
    if config.DEBUG:
        print('DEBUG dt_pattern',
            'date time (offset)',
            datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+3600*config.TS_OFFSET).strftime("%Y-%m-%d %H:%M"),
            'today',
            datetime.datetime.now().strftime("%Y-%m-%d"),
            'today (offset)',
            datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+3600*config.TS_OFFSET).strftime("%Y-%m-%d"),
            'yesterday (offset)',
            (datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+3600*config.TS_OFFSET) - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        )
    if period == 'today': return datetime.datetime.now().strftime("%Y-%m-%d")
    elif period == 'yesterday': return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
    # use offset
    # if period == 'today': #return(datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+3600*config.TS_OFFSET).strftime("%Y-%m-%d"))
    # elif period == 'yesterday': return (datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+3600*config.TS_OFFSET) - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
    elif period == 'this_month':
        return datetime.datetime.now().strftime("%Y-%m")
    elif period == 'this_year':
        return datetime.datetime.now().strftime("%Y")
    return ''


def _ts_pattern(period):
    ''' TEST: Alternative 1 '''
    ''' uses part of timestamp -- doesnt work very well  '''
    if period == 'today': return str(int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").timestamp()))[:4]
    elif period == 'yesterday': return str(int(datetime.datetime.strptime((datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "%Y-%m-%d").timestamp()))[:4]
    elif period == 'this_month': return str(int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m"), "%Y-%m").timestamp()))[:3]
    elif period == 'this_year':  return str(int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y"), "%Y").timestamp()))[:2]


#TODO: check date, needs to handle y/m/w rollovers (e.g. week falls in 2 diff months)
def pattern_from_date():
    ''' TEST: Alternative 2  calc week/month/year e.g. %y/09/*  %y/08/* -> 2026/0[8-9]/* '''
    now  = datetime.datetime.now()
    week_ago = now - datetime.timedelta(weeks = 1)
    dates = [(week_ago + datetime.timedelta(days=x)).strftime('%Y/%m') for x in range((now-week_ago).days + 1)]
    print(dates)
    #sorted_dates = sorted(dates, reverse=True)
    uniq_dates = list(set(dates))
    print(uniq_dates)
    #years = list(set([y.split('/')[0] for y in sorted_dates]))
    #months = list(set([m.split('/')[1] for m in sorted_dates]))
    #years = list(set([y.split('/')[0] for y in dates]))
    #months = list(set([m.split('/')[1] for m in dates]))
    #print(dates)
    #print(years)
    #print(months)
    #if len(years) > 1:
    #    years = '{' + ','.join(years) + '}'
    #else:
    #    years = years[0]
    #if len(months) > 1:
    #    months = '{' + ','.join(months) + '}'
    #else:
    #    months = months[0]
    #print(f'{config.WEBDIR}/json/{years}/{months}/*/*.json')
    #print(glob.glob(f'{config.WEBDIR}/json/{years}/{months}/*/*.json', recursive=True)
    #print(tmp)
    #print('DEBUG: fpath_date week', unique_dates)
    #print('DEBUG: fpath_date week', unique_years)
    #print('DEBUG: fpath_date week', result)


def messages_below_limit(period, num_messages=0):
    ''' Check if number of messages exceeds limit for period (plus margin) '''
    ''' Messages are received from broker every 5 minutes '''
    max_messages = 0
    num_daily_messages = 60/5 * 24
    margin = num_daily_messages
    if period == 'today': max_messages = num_daily_messages+margin/2
    if period == 'yesterday': max_messages = num_daily_messages+margin/2
    # TODO: if period == 'week':  max_messages = num_daily_messages*7+margin
    if period == 'this_month': max_messages = num_daily_messages*31+margin*2
    if period == 'this_year': max_messages = num_daily_messages*365+margin*3
    if max_messages > 0 and num_messages > max_messages:
        return False
    return True


# TODO: check for filename/timestamp ?
def check_fn_ts(period, fn):
    fn_dt = helper.dt_obj(int(fn.split('/')[-1].split('.')[0]), False)
    if (period in ['week', 'month', 'year'] and not helper.is_days_ago(fn_dt, period)):
        return False
    return True


# TODO: move glob to write_data() and change to **/*.json + check ts for 1 year ago
def read_files(period):
    data = {}
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/{fpath_pattern(period)}/*.json', recursive=True), reverse=True):
        if config.DEBUG:
            print(f'DEBUG: read_files period={period} fn={fn}')
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f_json:
                payload = f_json.read()
            try:
                inverter_ts = inverter_timestamp(payload)
                if not inverter_ts:
                    continue
                payload_obj = json.loads(payload)
                dt = helper.dt_obj(inverter_ts, True)
                if (period in ['today', 'yesterday', 'week', 'month', 'year'] and not helper.is_days_ago(dt, period)):
                    continue
                data[dt] = payload_obj
                data[dt]['fn'] = fn.removeprefix('./').split('/', 1)[1]
            except (KeyError, IndexError) as e:
                pass
        except json.decoder.JSONDecodeError as e:
            print(f'ERROR: decoding JSON from file "{fn}" - "{e}"')
    return data


# TODO: speed up globbing json files [dt]['fn'] -- turned off for now, getting fpath from timestamp instead
def db_query(period, path=None, key=None):
    ''' Query database '''
    data = {}
    if path:
        result = db.query_ts_json_path(f'{dt_pattern(period)}%', f'$.NOTIFICATION.{config.INVERTER_ID}', key)
    else:
        result = db.query_dt(f'{dt_pattern(period)}%')
    print('DEBUG: db_query messages_below_limit', period, len(result), f'{dt_pattern(period)}%', messages_below_limit(period, len(result)))
    if (period in config.USE_PERIODS and not messages_below_limit(period, len(result))):
        return data
    for localtime, timestamp, payload in result:
        #print('DEBUG: db_query', period, localtime, timestamp, payload)
        #exit(0)
        try:
            if not timestamp:
                continue
            if not payload:
                continue
            inverter_ts = inverter_timestamp(payload)
            if not inverter_ts:
                continue
            payload_obj = json.loads(payload)
            dt = helper.dt_obj(inverter_ts, True)
            if (period in config.USE_PERIODS and not helper.is_days_ago(dt, period)):
                continue
            if key:
                data[dt] = {key: payload}
            else:
                data[dt] = payload_obj
                data[dt]['fn'] = f'json/{dt.strftime("%Y/%m/%d")}/{timestamp}.json'
                #glob_result = glob.glob(f'{config.WEBDIR}/json/*/*/*/{str(timestamp)[:7]}*.json')
                #fn = max(glob_result) if glob_result else f'json/{dt.strftime("%Y/%m/%d")}/{timestamp}.json'
                #data[dt]['fn'] = fn.removeprefix('./').split('/', 1)[1]
                if config.DEBUG:
                    print('DEBUG: db_query fn', period, timestamp, data[dt]['fn'])
                    #print('DEBUG: db_query glob', period, timestamp, str(timestamp)[:8], glob_result[0], data[dt]['fn'])
        except (KeyError, IndexError) as e:
            pass
    return data


def get(period):
    ''' Get json data from files or db '''
    data = {}
    if period:
        #print(f'DEBUG: message get period={period} fpath_pattern={fpath_pattern(period)} dt_pattern={dt_pattern(period)}')
        if config.USE_DB:
            data = db_query(period)
        elif config.USE_FILES:
            data = read_files(period)
    return data
