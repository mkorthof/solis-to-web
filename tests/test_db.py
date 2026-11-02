import os
import sqlite3
import tempfile
import unittest

import db


class DatabaseTests(unittest.TestCase):
    def test_db_query_raises_on_malformed_sql(self):
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                db.create_table()
                db.insert(1700000001, '{"a": 1}')
                db.insert(1700000002, '{"a": 2}')

                with self.assertRaises(sqlite3.OperationalError):
                    db.query()
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
