import config
import message

import sqlite3
import glob
import json


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
    for fn in sorted(glob.glob(f'{config.WEBDIR}/json/*.json', recursive=True), reverse=True):
        try:
            with open(fn, 'r', encoding='utf-8', errors='ignore') as f_json:
                payload = f_json.read()
                try:

                    timestamp = message.inverter_ts(payload)
                    try:
                        with sqlite3.connect('solis.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", 
                                           (timestamp, payload))
                    except sqlite3.IntegrityError as e:
                        print(f'DEBUG: db - integrity error: {e} ("{timestamp}")')
                        pass
                    except sqlite3.Error as e:
                        print('ERROR:', e)
                        #print("DEBUG: db - failed to read data from table", e)
                        pass
                    finally:
                        if conn:
                            conn.close()
                            #print("DEBUG: db - the sqlite connection is closed")
                except (KeyError, IndexError, TypeError) as e:
                    print(f'ERROR: {e} (fn={fn}')
                    pass
        except json.decoder.JSONDecodeError as e:
            print(f'ERROR: decoding JSON from file "{fn}" - "{e}"')            


def insert(timestamp, payload):
    try:
        with sqlite3.connect('solis.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", 
                        (timestamp, payload))
    except sqlite3.IntegrityError as e:
        #print(f'DEBUG: db - integrity error: {e} ("{datetime}")')
        pass
    except sqlite3.Error as e:
        print('ERROR: database', e)
        pass
    finally:
        if conn:
            conn.close()


def query_json_path(ts, path, key=''):
    ''' Query DB using json path '''
    with sqlite3.connect('solis.db') as conn:
        if key:
            path = '.'.join([path, key])
        cursor = conn.cursor()
        #WHERE timestamp BETWEEN '{int(ts)-1}' AND '{int(ts)+1}'
        cursor.execute(f'''SELECT timestamp, json_extract(payload, '{path}')
                        FROM messages
                        WHERE timestamp LIKE '{ts}'
                        ORDER BY timestamp
                        ''')
        records = cursor.fetchall()
        cursor.close()
        #conn.close()
        return records
