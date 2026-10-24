import config
import message
import datetime
import glob
import re

import plot
import web
import os
import shutil


''' Helper Functions '''


def dt_obj(ts, offset=False):
    ''' Return datetime obj '''
    if offset:
        return datetime.datetime.fromtimestamp(ts+3600*config.TS_OFFSET)
    else:
        return datetime.datetime.fromtimestamp(ts)


def fmt_date_time():
    ''' Return current date and time as string '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fmt_timestamp(ts, offset=False):
    ''' Return timestamp as int '''
    if offset:
        return int(datetime.datetime.fromtimestamp(ts+3600*config.TS_OFFSET).timestamp())
    else:
        return int(datetime.datetime.fromtimestamp(ts).timestamp())


def fmt_timestamp_now():
    ''' Return current ts as int '''
    return int(datetime.datetime.now().timestamp())


def fpath_today():
    ''' Return date for today as str for file path '''
    return datetime.datetime.now().strftime("%Y/%m/%d")


def fpath_yesterday ():
    ''' Return date for yesterday as str for file path '''
    return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y/%m/%d")


# def fn_today():
#     ''' Return "date-filename.json" as str '''
#     return f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}-solis.json'


# def fn_yesterday():
#    ''' Return "date-filename.json" for yesterday as str '''
#     return f'{(datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y%m%d")}-solis.json'


# def last_message(period):
#     ''' Return dict with prefix date and filename '''
#     try:
#         fn = max(glob.glob(f'{config.WEBDIR}/json/{fn_date(period)}*-solis.json'))
#         return({'pf': fn.split('/')[-1].split('-')[0],
#                 'fn': fn.split('/')[-1]} if fn else None)
#     except IndexError as e:
#         print(f'ERROR: get last message filename - {e}')


def is_days_ago(date, period):
    ''' Return true if date is max_days ago or less '''
    max_days = 730
    if period == 'today':  max_days = 0
    if period == 'yesterday': max_days = 1
    if period == 'week': max_days = 7
    if period == 'month': max_days = 31
    if period == 'year': max_days = 365
    if (datetime.datetime.now() - date).days <= max_days:
        return True
    return False


def is_valid_filename(fn):
    if re.search(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", fn):
        #print(f'DEBUG: invalid filename "{plot_fn}"')
        return False
    return True


def mask(str):
    if config.MASK:
        char = "*"
        match = re.match(r'(.*)([0-9A-Z]{16}|\d{10})(.*)', str)
        if match[2]:
            return f'{match[1]}{(len(match[2])-4)*char+match[2][-4:]}{match[3]}'
    return str


def fmt_last_updated(time):
   ''' Return time since late update -- moved to helper.js '''
   sec = (datetime.datetime.now() - time).seconds
   if sec > 3600:
       return f'{round(sec/3600)} hours'
   elif sec > 60:
       return f'{round(sec/60)} minutes'
   return f'{sec} seconds'


def divide(value, divisor, num):
    ''' Convert unit by dividing value (e.g. W to kW) '''
    try:
        return(int(value[num])/divisor if isinstance(value, list) else int(value)/divisor)
    except (KeyError, ValueError, TypeError):
        pass
    return value


def conv_fn(apply):
    ''' Convert fn YYYYmmdd_MMHHSS-solis.json to fn with path:  YYYY/mm/dd/timestamp.json '''
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/*-solis.json')):
        f_date, f_time = fn.split('/')[-1].split('-')[0].split('_')
        f_datetime = f'{f_date}{f_time}'
        dt_obj = datetime.datetime.strptime(f_datetime, "%Y%m%d%H%M%S")
        timestamp = int(dt_obj.timestamp())
        newdir = f'{config.WEBDIR}/json/{dt_obj.strftime("%Y/%m/%d")}'
        if apply:
            os.makedirs(newdir, exist_ok=True)
            os.rename(fn, f'{newdir}/{timestamp}.json')
        print(f'INFO: convert_fn apply={apply} makedirs {newdir} rename {fn.split('/')[-1]} -> \
                {newdir}/{timestamp}.json  (f_date={f_date} f_time={f_time})')
    if not apply:
        print('\nINFO: dry-run, rerun with "--apply" to actually move files')

def data_yesterday(data):
    ''' Return yesterdays yield '''
    #return [vals['E_TODAY'] for _, vals in message.get('yesterday').items()][0]
    return list(data['yesterday'].values())[-1] if data.get('yesterday') else {}

def webdirs():
    ''' Create dirs and copy static files '''
    if not os.path.isdir(f'{config.WEBDIR}'):
        os.mkdir(f'{config.WEBDIR}')
    for dir in ['json', 'plot']:
        if not os.path.isdir(f'{config.WEBDIR}/{dir}'):
            os.mkdir(f'{config.WEBDIR}/{dir}')
    if not os.path.isfile(f'{config.WEBDIR}/plotly.min.js'):
        shutil.copyfile('plotly.min.js', f'{config.WEBDIR}/plotly.min.js')
    if config.WEBSTATIC:
        if not os.path.isdir(f'{config.WEBDIR}/static'):
            os.mkdir(f'{config.WEBDIR}/static') 
        for fpath in config.WEBSTATIC_FILES:
            shutil.copyfile(fpath, f'{config.WEBDIR}/static/{os.path.basename(fpath)}')


def write_data(payload):
    ''' Get data from json. Generate and write index, plot and message as html files '''
    data = {}
    for period in config.USE_PERIODS:
        data[period] = message.get(period)
    for period in ['today', 'yesterday'] + config.LINK_PLOT_PERIODS:
        for plot_key in config.PLOTS:
            plot_values = plot.values(period, plot_key, data[period])
            plot.write_plot(period, plot_key, plot_values)
    for period in ['today'] + config.LINK_PREVIOUS_MESSAGES:
        with open(f'{config.WEBDIR}/messages_{period}.html', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(web.messages_html(period, data[period]))
    with open(f'{config.WEBDIR}/plots_all.html', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(web.plots_all_html(config.USE_PERIODS)) 
    with open(f'{config.WEBDIR}/index.html', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(web.index_html(payload, {'today': data['today'], 'yesterday': data['yesterday']}))

