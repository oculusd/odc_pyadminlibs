# Copyright (c) 2019. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""Testing all domain aggregates

Depends on the Python package "coverage"

Usage

::

    $ coverage run  --omit="*tests*,*venv*" -m tests.test_all
    $ coverage report -m
"""
import unittest
from tests.test_persistence import TestPersistenceInit


def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestPersistenceInit('test_sql_get_connection_positive_01'))
    suite.addTest(TestPersistenceInit('test_sql_get_connection_negative_01'))
    suite.addTest(TestPersistenceInit('test_create_database_table_positive_01'))
    suite.addTest(TestPersistenceInit('test_create_database_table_negative_01'))
    suite.addTest(TestPersistenceInit('test_adapt_decimal'))
    suite.addTest(TestPersistenceInit('test_convert_decimal'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())


# EOF
