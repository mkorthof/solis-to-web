import os
import tempfile
import unittest

import db


class DatabaseTests(unittest.TestCase):
    def test_query_returns_records_newest_first(self):
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                db.create_table()
                db.insert(1700000001, '{"a": 1}')
                db.insert(1700000002, '{"a": 2}')

                self.assertEqual(
                    db.query(),
                    [
                        (1700000002, '{"a": 2}'),
                        (1700000001, '{"a": 1}'),
                    ],
                )
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
