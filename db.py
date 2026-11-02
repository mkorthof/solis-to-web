import config

import sqlite3


''' Database functions '''


def create_table():
    ''' Create db with messages table '''
    try:
        with sqlite3.connect(config.FN_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE messages (
                    timestamp   INTEGER PRIMARY KEY UNIQUE,
                    payload     TEXT NOT NULL
                )
            """)
    except sqlite3.Error as e:
        print(f'ERROR: create, sqlite3.Error "{e}"')
    finally:
        if conn:
            conn.close()


def insert(ts, payload):
    try:
        with sqlite3.connect(config.FN_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", (ts, payload))
    except sqlite3.IntegrityError as e:
        #print(f'ERROR: delete timestamp={ts}, sqlite3.IntegrityError "{e}"')
        pass
    except sqlite3.Error as e:
        print(f'ERROR: insert, sqlite3.Error "{e}"')
    finally:
        if conn:
            conn.close()


def delete_ts(ts):
    try:
        with sqlite3.connect(config.FN_DB) as conn:
                cursor = conn.cursor()  
                cursor.execute("""
                    DELETE FROM messages
                    WHERE timestamp = ?
                """, (ts,))
                cursor.close()
    except sqlite3.IntegrityError as e:
        print(f'ERROR: delete timestamp={ts}, sqlite3.IntegrityError "{e}"')
    except sqlite3.Error as e:
        print(f'ERROR: insert, sqlite3.Error "{e}"')
    finally:
        if conn:
            conn.close()


def query():
    ''' Query DB '''
    records = {}
    with sqlite3.connect(config.FN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, payload
            FROM messages
            ORDER BY timestamp DESC
        """)
        records = cursor.fetchall()
        cursor.close()
        #conn.close()
        return records


def query_ts(ts):
    records = {}
    with sqlite3.connect(config.FN_DB) as conn:
        cursor = conn.cursor()  
        cursor.execute("""
            SELECT *
            FROM messages
            WHERE timestamp = ?
        """, (ts,))
        records = cursor.fetchall()
        cursor.close()
        return records


def query_dt(dt_pattern):
    ''' Query DB with datetime pattern '''
    records = {}
    with sqlite3.connect(config.FN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM messages
            WHERE datetime(timestamp, 'unixepoch', 'localtime') LIKE ?
            ORDER BY timestamp DESC
        """, (dt_pattern,))
        records = cursor.fetchall()
        cursor.close()
        return records


def query_ts_json_path(ts, path, key=''):
    ''' Query DB using json path '''
    records = {}
    with sqlite3.connect(config.FN_DB) as conn:
        if key:
            path = '.'.join([path, key])
        cursor = conn.cursor()
        #WHERE timestamp BETWEEN '{int(ts)-1}' AND '{int(ts)+1}'
        cursor.execute("""
            SELECT timestamp, json_extract(payload, :path)
            FROM messages
            WHERE timestamp LIKE :ts
            ORDER BY timestamp DESC
        """, (path, ts))
        records = cursor.fetchall()
        cursor.close()
        return records
