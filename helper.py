import config

import datetime
import glob
import re

def fmt_date():
    ''' Return current date and time '''
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fmt_timestamp(ts):
    ''' Return timestamp in human-readable format '''
    return (datetime.datetime.fromtimestamp(ts+3600*config.TS_OFFSET))


def prefix_date(period):
    ''' Return file date prefix '''
    if period == 'now':
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    elif period == 'today':
        return datetime.datetime.now().strftime("%Y%m%d")
    elif period == 'yesterday':
        return (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y%m%d")
    elif period == 'month':
        return (datetime.datetime.now().strftime("%Y%m"))
    elif period == 'year':
        return (datetime.datetime.now().strftime("%Y"))
    elif period == 'this_month':
        return (datetime.datetime.now().strftime("%Y%m"))
    elif period == 'this_year':
        return (datetime.datetime.now().strftime("%Y"))


def get_last_message(period):
    ''' Return dict with prefix date and filename '''
    try:
        fn = max(glob.glob(f'{config.WEBDIR}/json/{prefix_date(period)}*-solis.json'))
        return({'pf': fn.split('/')[-1].split('-')[0],
                'fn': fn.split('/')[-1]}
                if fn else None)
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
        chr = "*"
        match = re.match(r'(.*)([0-9A-Z]{16})(.*)', str)
        if match[2]:
            return f'{match[1]}{(len(match[2])-4)*chr+match[2][-4:]}{match[3]}'
    return str


# replaced by helper.js
def fmt_last_updated(time):
    ''' Return time since late update '''
    sec = (datetime.datetime.now() - time).seconds
    if sec > 3600:
        return f'{round(sec/3600)} hours'
    elif sec > 60:
        return f'{round(sec/60)} minutes'
    return f'{sec} seconds'
