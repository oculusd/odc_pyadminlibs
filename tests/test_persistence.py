# Copyright (c) 2019. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run --omit="*tests*,*venv*" -m tests.test_persistence
    $ coverage report -m
"""

import unittest
import logging
from odc_pycommons import OculusDLogger, DEBUG, formatter, get_utc_timestamp
from pathlib import Path
import os
import traceback
import time
import tempfile
from decimal import Decimal
import sqlite3
from odc_pyadminlibs.persistence import sql_get_connection
from odc_pyadminlibs.persistence import create_database_table
from odc_pyadminlibs.persistence import adapt_decimal
from odc_pyadminlibs.persistence import convert_decimal
from odc_pyadminlibs.persistence.root_account_persistence import create_root_account_table
from odc_pyadminlibs.persistence.root_account_persistence import create_root_account
from odc_pyadminlibs.persistence.root_account_persistence import get_root_account
from odc_pyadminlibs.persistence.root_account_persistence import update_root_account
from odc_pyadminlibs.persistence.root_account_persistence import get_root_account_ids


DB_TEST_DIR = tempfile.gettempdir()


class TestLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.lines = list()

    def emit(self, record):
        self.lines.append(self.format(record))

    def flush(self):
        self.lines = list()

class TestPersistenceInit(unittest.TestCase):

    def setUp(self):
        self.test_database_file = 'test_database.sqlite'
        self.test_database_path = Path('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))
        if self.test_database_path.is_file():
            os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))
        self.conn = None

        # Setup the test logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = TestLogHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)
        self.test_logger = OculusDLogger(logger_impl=self.logger)

    def tearDown(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        if os.path.exists(self.test_database_path):
            if self.test_database_path.is_file:
                os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))

    def test_sql_get_connection_positive_01(self):
        self.conn = sql_get_connection(data_path=DB_TEST_DIR, data_file=self.test_database_file)
        self.assertIsNotNone(self.conn)
        self.assertTrue(self.test_database_path.is_file)

    def test_sql_get_connection_negative_01(self):
        with self.assertRaises(Exception):
            self.conn = sql_get_connection(data_path='/XXXXXXXX', data_file=self.test_database_file, L=self.test_logger)
        self.assertTrue('EXCEPTION' in self.ch.lines[1])

    def test_create_database_table_positive_01(self):
        create_database_table(
            database_table_name='my_test_table',
            database_table_definition='some_id integer primary key, some_name text',
            persistence_path=DB_TEST_DIR,
            persistence_file=self.test_database_file,
            L=self.test_logger
        )
        self.assertEqual(len(self.ch.lines), 2)
        self.assertTrue('INFO' in self.ch.lines[0])
        self.assertTrue('Created table' in self.ch.lines[1])

    def test_create_database_table_negative_01(self):
        with self.assertRaises(Exception):
            create_database_table(
                database_table_name='my_test_table',
                database_table_definition='some_id integer primary key\b\b, some_name text',
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
        self.assertTrue('EXCEPTION' in self.ch.lines[1])

    def test_adapt_decimal(self):
        self.assertTrue(adapt_decimal(Decimal(22/7)).startswith('3.14'))

    def test_convert_decimal(self):
        d = Decimal('0.99')
        self.assertTrue(convert_decimal('0.99').compare(d) == 0)


class TestRootAccountPersistence(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.test_database_file = 'test_database.sqlite'
        self.test_database_path = Path('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))
        if self.test_database_path.is_file():
            os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))
        self.conn = None

        # Setup the test logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = TestLogHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)
        self.test_logger = OculusDLogger(logger_impl=self.logger)

    @classmethod
    def tearDownClass(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        if os.path.exists(self.test_database_path):
            if self.test_database_path.is_file:
                os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))

    def test_create_root_account_table_positive_01(self):
        test_database_path = Path('{}{}{}'.format(DB_TEST_DIR, os.sep, 'unique_db_0001.sqlite'))
        if os.path.exists(test_database_path):
            if self.test_database_path.is_file:
                os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, 'unique_db_0001.sqlite'))
        if os.path.exists(test_database_path):
            self.fail('Failed to remove temporary test database file')

        table_created = create_root_account_table(
            persistence_path=DB_TEST_DIR,
            persistence_file='unique_db_0001.sqlite',
            L=self.test_logger
        )
        self.assertTrue(table_created)

        root_account_table_found = False
        conn = sqlite3.connect('{}{}{}'.format(DB_TEST_DIR, os.sep, 'unique_db_0001.sqlite'))
        c = conn.cursor()
        for row in c.execute('select name from sqlite_master where type = ?', ('table',)):
            if row[0] == 'root_account':
                root_account_table_found = True
        conn.commit()
        conn.close()

        self.assertTrue(root_account_table_found)
        
        if os.path.exists(test_database_path):
            if self.test_database_path.is_file:
                os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, 'unique_db_0001.sqlite'))
        if os.path.exists(test_database_path):
            self.fail('Failed to remove temporary test database file')

    def test_create_root_account_positive_01(self):
        table_created = create_root_account_table(persistence_path=DB_TEST_DIR, persistence_file=self.test_database_file, L=self.test_logger)
        self.assertTrue(table_created)

        root_account = 'some data representing a root account'
        root_account_create_result = create_root_account(
            root_account_id='test001',
            root_account=root_account,
            persistence_path=DB_TEST_DIR,
            persistence_file=self.test_database_file,
            L=self.test_logger
        )

        self.assertTrue(root_account_create_result)

        conn = sqlite3.connect(str(self.test_database_path))
        c = conn.cursor()
        for row in c.execute('select count(*) from root_account where root_account_id = ?', ('test001',)):
            self.assertTrue(int(row[0] > 0))
        conn.commit()
        conn.close()

    def test_get_root_account_positive_01(self):
        table_created = create_root_account_table(persistence_path=DB_TEST_DIR, persistence_file=self.test_database_file, L=self.test_logger)
        self.assertTrue(table_created)

        root_accounts = list()
        root_account_strings = list()
        for id in range(1,9):
            root_account_id = 'get_test_{}'.format(id)
            root_account = 'some data representing a root account - id={}'.format(id)
            root_accounts.append(root_account_id)
            root_account_strings.append(root_account)
            root_account_create_result = create_root_account(
                root_account_id=root_account_id,
                root_account=root_account,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertTrue(root_account_create_result, 'Failed on account "{}"'.format(id))

        root_accounts_tested = 0
        for root_account_id in root_accounts:
            root_account_data_ref = root_account_strings[root_accounts_tested]
            root_accounts_tested += 1
            retrieved_root_account_data = get_root_account(
                root_account_id=root_account_id,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertEqual(root_account_data_ref, retrieved_root_account_data, 'Data mismatch for account "{}"'.format(root_account_id))

        self.assertEqual(root_accounts_tested, 8, 'Unexpected number of processed root accounts')

    def test_get_root_account_negative_01(self):
        retrieved_root_account_data = None
        with self.assertRaises(Exception):
            retrieved_root_account_data = get_root_account(
                root_account_id='not_existing_1',
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
        self.assertIsNone(retrieved_root_account_data)

    def test_update_root_account_positive_01(self):
        table_created = create_root_account_table(persistence_path=DB_TEST_DIR, persistence_file=self.test_database_file, L=self.test_logger)
        self.assertTrue(table_created)

        root_accounts = list()
        root_account_strings = list()
        for id in range(11,19):
            root_account_id = 'get_test_{}'.format(id)
            root_account = 'some data representing a root account - id={}'.format(id)
            root_accounts.append(root_account_id)
            root_account_strings.append(root_account)
            root_account_create_result = create_root_account(
                root_account_id=root_account_id,
                root_account=root_account,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertTrue(root_account_create_result, 'Failed on account "{}"'.format(id))

        for id in range(11,19):
            root_account_id = 'get_test_{}'.format(id)
            updated_root_account = 'UPDATED data representing a root account - id={}'.format(id)
            update_result = update_root_account(
                root_account_id=root_account_id,
                root_account=updated_root_account,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertTrue(update_result, 'Failed to updated ID "{}"'.format(id))

            retrieved_root_account_data = get_root_account(
                root_account_id=root_account_id,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertEqual(retrieved_root_account_data, updated_root_account, 'Updated data mismatch for id "{}"'.format(id))

    @unittest.skip('Skipping as an update to sqlite on a none-existing item does not throw an exception')
    def test_update_root_account_negative_01(self):
        table_created = create_root_account_table(persistence_path=DB_TEST_DIR, persistence_file=self.test_database_file, L=self.test_logger)
        self.assertTrue(table_created)
        update_result = update_root_account(
            root_account_id='not_existing_1',
            root_account='Any data will do',
            persistence_path=DB_TEST_DIR,
            persistence_file=self.test_database_file,
            L=self.test_logger
        )
        self.assertFalse(update_result)

    def test_get_root_account_ids(self):
        table_created = create_root_account_table(persistence_path=DB_TEST_DIR, persistence_file=self.test_database_file, L=self.test_logger)
        self.assertTrue(table_created)

        root_accounts = list()
        root_account_strings = list()
        for id in range(21,29):
            root_account_id = 'get_test_{}'.format(id)
            root_account = 'some data representing a root account - id={}'.format(id)
            root_accounts.append(root_account_id)
            root_account_strings.append(root_account)
            root_account_create_result = create_root_account(
                root_account_id=root_account_id,
                root_account=root_account,
                persistence_path=DB_TEST_DIR,
                persistence_file=self.test_database_file,
                L=self.test_logger
            )
            self.assertTrue(root_account_create_result, 'Failed on account "{}"'.format(id))

        all_ids = get_root_account_ids(
            persistence_path=DB_TEST_DIR,
            persistence_file=self.test_database_file,
            L=self.test_logger
        )
        found_ids = list()
        for id in all_ids:
            if id in root_accounts:
                found_ids.append(id)

        self.assertTrue(len(root_accounts) > 0)
        self.assertTrue(len(all_ids) > 0)
        self.assertTrue(len(found_ids) > 0)
        self.assertEqual(len(root_accounts), len(found_ids))



    

# EOF
