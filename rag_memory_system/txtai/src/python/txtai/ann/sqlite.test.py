import unittest
from unittest.mock import patch, MagicMock

from annlite.backends.sqlite import SQLite

class TestSQLite(unittest.TestCase):

    @patch('annlite.backends.sqlite.SQLITEVEC', False)
    def test_init_no_sqlitevec(self):
        with self.assertRaises(ImportError):
            SQLite({})

    @patch('annlite.backends.sqlite.SQLITEVEC', True)
    def test_init(self):
        config = {'dimensions': 128, 'table': 'test_table'}
        sqlite_ann = SQLite(config)
        self.assertEqual(sqlite_ann.config, config)
        self.assertIsNone(sqlite_ann.quantize)
        self.assertIsNone(sqlite_ann.connection)
        self.assertIsNone(sqlite_ann.cursor)
        self.assertEqual(sqlite_ann.path, "")

    @patch('annlite.backends.sqlite.SQLITEVEC', True)
    def test_load(self):
        config = {'dimensions': 128, 'table': 'test_table'}
        sqlite_ann = SQLite(config)
        path = 'test_path'
        sqlite_ann.load(path)
        self.assertEqual(sqlite_ann.path, path)

    @patch('annlite.backends.sqlite.SQLITEVEC', True)
    def test_save_new_path(self):
        config = {'dimensions': 128, 'table': 'test_table'}
        sqlite_ann = SQLite(config)
        sqlite_ann.path = 'old_path'
        new_path = 'new_path'
        sqlite_ann.connection = MagicMock()
        sqlite_ann.copy = MagicMock()
        sqlite_ann.save(new_path)
        sqlite_ann.copy.return_value.close.assert_called_once()

    @patch('annlite.backends.sqlite.SQLITEVEC', True)
    def test_close(self):
        config = {'dimensions': 128, 'table': 'test_table'}
        sqlite_ann = SQLite(config)
        sqlite_ann.connection = MagicMock()
        sqlite_ann.close()
        sqlite_ann.connection.close.assert_called_once()
        self.assertIsNone(sqlite_ann.connection)