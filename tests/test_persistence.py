# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run -m tests.test_persistence
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
from odc_pyadminlibs.persistence import sql_get_connection
from odc_pyadminlibs.persistence import create_database_table


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
        if self.test_database_path.is_file:
            os.remove('{}{}{}'.format(DB_TEST_DIR, os.sep, self.test_database_file))

    def test_sql_get_connection_positive_01(self):
        self.conn = sql_get_connection(data_path=DB_TEST_DIR, data_file=self.test_database_file)
        self.assertIsNotNone(self.conn)
        self.assertTrue(self.test_database_path.is_file)

    def test_create_database_table_positive_01(self):
        self.conn = sql_get_connection(data_path=DB_TEST_DIR, data_file=self.test_database_file)
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


    

# EOF
