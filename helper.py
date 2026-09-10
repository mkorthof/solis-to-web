import config
import message
import db

import datetime
import glob
import re
import plot
import web
import os
import shutil


def fmt_date():
    ''' Return current date and time '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fmt_datetime(ts, offset=False):
    if offset:
        return (datetime.datetime.fromtimestamp(ts+3600*config.TS_OFFSET))
    else:
        return (datetime.datetime.fromtimestamp(ts))


def fmt_timestamp(ts, offset=False):
    if offset:
        return (int(datetime.datetime.fromtimestamp(ts+3600*config.TS_OFFSET).timestamp()))
    else:
        return (int(datetime.datetime.fromtimestamp(ts).timestamp()))


def fn_now():
    ''' Return dated filename.json '''
    return (f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}-solis.json')


def fn_date(period):
    ''' Return date for period, used in glob for json files '''
    if period == 'today':
        return datetime.datetime.now().strftime("%Y%m%d")
    elif period == 'yesterday':
        return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y%m%d")
    elif period == 'week':
        return ''
    elif period == 'month':
        return ''
    elif period == 'year':
        return ''
    elif period == 'this_month':
        return (datetime.datetime.now().strftime("%Y%m"))
    elif period == 'this_year':
        return (datetime.datetime.now().strftime("%Y"))


# TODO: use new fn path format yyy/mm/dd/ts.json
#       handle period week, month, year (resursive glob)
#       add single def that takes 'period' and returns date pattern for both fn glob and db query

def _fpath_date(period):
    ''' Return date pattern for period, used in glob for json file and path '''
    if period == 'today':
        return datetime.datetime.now().strftime("%Y/%m/%d")
    elif period == 'yesterday':
        return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y/%m/%d")
    elif period == 'week':
        return ''
    elif period == 'month':
        #return (datetime.datetime.now().strftime("%Y/%m"))
        return ''
    elif period == 'year':
        #return (datetime.datetime.now().strftime("%Y"))
        return ''
    elif period == 'this_month':
        return (datetime.datetime.now().strftime("%Y/%m"))
    elif period == 'this_year':
        return (datetime.datetime.now().strftime("%Y"))


def db_date(period):
    ''' Return date pattern used in db query '''
    if period == 'now':
        #return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return int(datetime.datetime.now().timestamp())
    elif period == 'today':
        #return datetime.datetime.now().strftime("%Y-%m-%d")
        return str(int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").timestamp()))[:5]
    elif period == 'yesterday':
        #return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        return str(int(datetime.datetime.strptime((datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d"), "%Y-%m-%d").timestamp()))[:5]
    elif period == 'week':
        #return int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y"), "%Y").timestamp())
        return ''
    elif period == 'month':
    #    #return (datetime.datetime.now().strftime("%Y-%m"))
    #    return int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m"), "%Y-%m").timestamp())
        return ''
    elif period == 'year':
    #    #return (datetime.datetime.now().strftime("%Y"))
    #    return int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y"), "%Y").timestamp())
        return ''
    elif period == 'this_month':
    #    #return (datetime.datetime.now().strftime("%Y-%m"))
        return int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m"), "%Y-%m").timestamp())
    elif period == 'this_year':
    #    #return (datetime.datetime.now().strftime("%Y"))
        return int(datetime.datetime.strptime(datetime.datetime.now().strftime("%Y"), "%Y").timestamp())


def last_message(period):
    ''' Return dict with prefix date and filename '''
    try:
        fn = max(glob.glob(f'{config.WEBDIR}/json/{fn_date(period)}*-solis.json'))
        return({'pf': fn.split('/')[-1].split('-')[0],
                'fn': fn.split('/')[-1]} if fn else None)
    except IndexError as e:
        print(f'ERROR: get last message filename - {e}')


def is_days_ago(date, period):
    ''' Return true if date is max_days ago or less '''
    if period == 'week':
        max_days = 7
    if period == 'month':
        max_days = 31
    if period == 'year':
        max_days = 365
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
    ''' Return time since late update (moved to helper.js) '''
    sec = (datetime.datetime.now() - time).seconds
    if sec > 3600:
        return f'{round(sec/3600)} hours'
    elif sec > 60:
        return f'{round(sec/60)} minutes'
    return f'{sec} seconds'


def write_data():
    ''' Generate and write plot and message output as html files '''
    for period in ['today', 'yesterday'] + config.LINK_PLOT_PERIODS:
        for plot_key in config.PLOTS:
            data = message.history(period, plot_key)
            values = plot.values(period, plot_key, data)
            plot.write_plot(period, plot_key, values)
    for period in ['today'] + config.LINK_PREVIOUS_MESSAGES:
        with open(f'{config.WEBDIR}/messages_{period}.html', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(web.messages_html(period))


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


def divide(value, divisor, num):
    ''' Convert unit by dividing value (e.g. W to kW) '''
    try:
        return(int(value[num])/divisor if isinstance(value, list) else int(value)/divisor)
    except (KeyError, ValueError, TypeError):
        pass
    return(value)


def conv_fn():
    ''' Convert fn YYYYmmd_MMHHSS-solis.json to fn with path:  YYYY/mm/dd/timestamp.json '''
    print('INFO: dry run, not moving files..')
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/*-solis.json')):
        f_date, f_time = fn.split('/')[-1].split('-')[0].split('_')
        f_datetime = f'{f_date}{f_time}'
        dt_obj = datetime.datetime.strptime(f_datetime, "%Y%m%d%H%M%S")
        timestamp = int(dt_obj.timestamp())
        newdir = f'{config.WEBDIR}/json/{dt_obj.strftime("%Y/%m/%d")}'
        #os.makedirs({newdir, exist_ok=True)
        #os.rename(fn, f'{newdir}/{timestamp}.json'}
        print(f'DEBUG: convert_fn makedirs {newdir} rename {fn.split('/')[-1]} -> {newdir}/{timestamp}.json  (f_date={f_date} f_time={f_time})')

