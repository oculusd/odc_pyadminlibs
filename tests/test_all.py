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
from tests.test_persistence import TestRootAccountPersistence
from tests.test_actions import TestRegisterRootAccount
from tests.test_actions import TestPing


def suite():
    suite = unittest.TestSuite()

    # TestPersistenceInit
    suite.addTest(TestPersistenceInit('test_sql_get_connection_positive_01'))
    suite.addTest(TestPersistenceInit('test_sql_get_connection_negative_01'))
    suite.addTest(TestPersistenceInit('test_create_database_table_positive_01'))
    suite.addTest(TestPersistenceInit('test_create_database_table_negative_01'))
    suite.addTest(TestPersistenceInit('test_adapt_decimal'))
    suite.addTest(TestPersistenceInit('test_convert_decimal'))

    # TestRootAccountPersistence 
    suite.addTest(TestRootAccountPersistence('test_create_root_account_table_positive_01'))
    suite.addTest(TestRootAccountPersistence('test_create_root_account_positive_01'))
    suite.addTest(TestRootAccountPersistence('test_get_root_account_positive_01'))
    suite.addTest(TestRootAccountPersistence('test_get_root_account_negative_01'))
    suite.addTest(TestRootAccountPersistence('test_update_root_account_positive_01'))
    suite.addTest(TestRootAccountPersistence('test_update_root_account_negative_01'))
    suite.addTest(TestRootAccountPersistence('test_get_root_account_ids'))

    # TestPersistenceInit
    suite.addTest(TestRegisterRootAccount('test_register_root_account_positive_01'))
    suite.addTest(TestRegisterRootAccount('test_register_root_account_fail_to_create_root_account_table_01'))
    suite.addTest(TestRegisterRootAccount('test_register_root_account_remote_service_error_01'))
    suite.addTest(TestRegisterRootAccount('test_register_root_account_invalid_response_dict_causing_exception_01'))

    # TestPing
    suite.addTest(TestPing('test_ping_positive_01'))
    suite.addTest(TestPing('test_ping_invalid_return_data_causing_exception_01'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())


# EOF
