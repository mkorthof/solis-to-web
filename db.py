import config

import sqlite3
from contextlib import closing


''' Database functions '''


def create_table():
    ''' Create db with messages table '''
    try:
        with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
            conn.execute("""
                CREATE TABLE messages (
                    timestamp   INTEGER PRIMARY KEY UNIQUE,
                    payload     TEXT NOT NULL
                )
            """)
    except sqlite3.Error as e:
        print(f'ERROR: db create, sqlite3.Error "{e}"')


def insert(ts, payload):
    try:
        with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
            conn.execute("INSERT INTO messages (timestamp, payload) VALUES (?, ?)", (ts, payload))
    except sqlite3.IntegrityError as e:
        if bool(config.DEBUG):
            print(f'DEBUG: db insert ts={ts} sqlite3.IntegrityError "{e}"')
    except sqlite3.Error as e:
        print(f'ERROR: db insert, sqlite3.Error "{e}"')


def replace(ts, payload):
    try:
        with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
            conn.execute("INSERT OR REPLACE INTO messages (timestamp, payload) VALUES (?, ?)", (ts, payload))
    except sqlite3.IntegrityError as e:
        pass
    except sqlite3.Error as e:
        print(f'ERROR: db insert, sqlite3.Error "{e}"')


def delete_ts(ts):
    try:
        with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
            conn.execute("""
                DELETE FROM messages
                WHERE timestamp = ?
            """, (ts,))
    except sqlite3.IntegrityError as e:
        print(f'ERROR: db delete timestamp={ts}, sqlite3.IntegrityError "{e}"')
    except sqlite3.Error as e:
        print(f'ERROR: db insert, sqlite3.Error "{e}"')


def query():
    ''' Query DB '''
    records = {}
    with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
            cursor = conn.execute("""
                SELECT timestamp, payload
                FROM messages
                ORDER BY timestamp DESC
            """)
            records = cursor.fetchall()
            return records


def query_ts(ts):
    records = {}
    with sqlite3.connect(config.FN_DB) as conn, conn:
        cursor = conn.execute("""
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
    with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
        cursor = conn.execute("""
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
    with closing(sqlite3.connect(config.FN_DB)) as conn, conn:
        if key:
            path = '.'.join([path, key])
        # WHERE timestamp BETWEEN '{int(ts)-1}' AND '{int(ts)+1}'
        cursor = conn.execute("""
            SELECT timestamp, json_extract(payload, :path)
            FROM messages
            WHERE timestamp LIKE :ts
            ORDER BY timestamp DESC
        """, (path, ts))
        records = cursor.fetchall()
        cursor.close()
        return records
