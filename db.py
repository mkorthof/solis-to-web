import config
import helper
import message

import sqlite3
import glob
import json


''' Database '''


def create_table():
    with sqlite3.connect('solis.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE messages (
                timestamp   INTEGER PRIMARY KEY UNIQUE,
                payload     TEXT NOT NULL
            );
        ''')


def import_json():
    ''' Import *.json '''
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/**/*.json', recursive=True), reverse=True):
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f_json:
                payload = f_json.read()
                try:
                    ts = message.inverter_timestamp(payload) if message.inverter_timestamp(payload) else helper.fmt_timestamp_now()
                    try:
                        with sqlite3.connect('solis.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", 
                                           (ts, payload))
                    except sqlite3.IntegrityError as e:
                        print(f'ERROR: integrity timestamp={ts}', e)
                    except sqlite3.Error as e:
                        print('ERROR: sqlite', e)
                    finally:
                        if conn:
                            conn.close()
                except (KeyError, IndexError, TypeError) as e:
                    print(f'ERROR: import fn={fn} ts={ts}', e)
        except json.decoder.JSONDecodeError as e:
            print(f'ERROR: decode fn={fn}', e) 


def insert(timestamp, payload):
    try:
        with sqlite3.connect('solis.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", 
                        (timestamp, payload))
    except sqlite3.IntegrityError as e:
        #print(f'ERROR: integrity timestamp={timestamp}', e)
        pass
    except sqlite3.Error as e:
        print('ERROR: sqlite', e)
        pass
    finally:
        if conn:
            conn.close()


def query():
    ''' Query DB '''
    with sqlite3.connect('solis.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT timestamp, payload
                        FROM messages
                        SELECT *
                        ORDER BY timestamp DESC;
                        ''')
        records = cursor.fetchall()
        cursor.close()
        #conn.close()
        return records



def query_dt(dt_pattern):
    ''' Query DB with datetime pattern '''
    with sqlite3.connect('solis.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'''SELECT datetime(timestamp, 'unixepoch', 'localtime') as localtime, *
                        FROM messages
                        WHERE localtime LIKE '{dt_pattern}'
                        ORDER BY timestamp DESC;
                        ''')
        records = cursor.fetchall()
        cursor.close()
        return records


def query_ts_json_path(ts, path, key=''):
    ''' Query DB using json path '''
    with sqlite3.connect('solis.db') as conn:
        if key:
            path = '.'.join([path, key])
        cursor = conn.cursor()
        #WHERE timestamp BETWEEN '{int(ts)-1}' AND '{int(ts)+1}'
        cursor.execute(f'''SELECT timestamp, json_extract(payload, '{path}')
                        FROM messages
                        WHERE timestamp LIKE '{ts}'
                        ORDER BY timestamp DESC;
                        ''')
        records = cursor.fetchall()
        cursor.close()
        return records
