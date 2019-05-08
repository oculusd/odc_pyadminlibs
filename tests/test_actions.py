# Copyright (c) 2019. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run --omit="*tests*,*venv*" -m tests.test_actions
    $ coverage report -m
"""

import unittest
from unittest.mock import MagicMock
from unittest.mock import Mock
import logging
from odc_pyadminlibs import Configuration, PersistenceConfiguration, CommsConfiguration
from odc_pycommons import OculusDLogger, DEBUG, formatter, get_utc_timestamp
from odc_pycommons.models import CommsResponse
from pathlib import Path
import os
import traceback
import time
import tempfile
from decimal import Decimal
import json
from odc_pyadminlibs.actions.register import root_account_registration
from odc_pyadminlibs.actions.ping import check_service_response


class TestLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.lines = list()

    def emit(self, record):
        self.lines.append(self.format(record))

    def flush(self):
        self.lines = list()


class TestRegisterRootAccount(unittest.TestCase):

    def setUp(self):

        # Setup the test logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        ch = TestLogHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        test_logger = OculusDLogger(logger_impl=logger)

        positive_comms_response = CommsResponse(
            is_error=False,
            response_code=1,
            response_code_description=None,
            response_data=json.dumps(
                {
                    'Data': {
                        'RootAccountId': 'ra111111',
                        'RootAccountStatus': 'PENDING'
                    },
                    'ErrorMessage': None,
                    'IsError': False,
                    'Message': 'RootAccount created successfully',
                    'TraceId': '1111-2222-3333-4444'
                }
            ),
            trace_id=None
        )
        comms_configuration = CommsConfiguration(
            service_handlers={
                'GetServiceUri': MagicMock(return_value='http://localhost/'),
                'Get': None,
                'JsonPost': MagicMock(return_value=positive_comms_response),
            },
            service_region='us1'
        )
        persistence_configuration = PersistenceConfiguration(
            persistence_path=tempfile.gettempdir(),
            persistence_file='accounts',
            flags={
                'PersistPassphrase': True,
                'PersistOnSuccess': True,
            }
        )
        self.configuration = Configuration(
            persistence_configuration=persistence_configuration,
            comms_configurations=comms_configuration,
            logger=test_logger
        )
        if Path(self.configuration.persistence_configuration.persistence_full_path).is_file():
            os.remove(self.configuration.persistence_configuration.persistence_full_path)
        self.conn = None

    def test_register_root_account_positive_01(self):
        """This test aims to verify the return data structure of a guarenteed positive result.
        """
        result = root_account_registration(
            email_address='test@example.tld',
            passphrase='111 abcdefghijklm 222 *',
            account_name='unittest',
            configuration=self.configuration,
            trace_id=None
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('IsError' in result)
        self.assertTrue('TraceId' in result)
        self.assertTrue('RemoteTraceId' in result)
        self.assertTrue('ErrorMessage' in result)
        self.assertTrue('Message' in result)
        self.assertTrue('RootAccountObj' in result)
        self.assertIsInstance(result['IsError'], bool)
        self.assertIsNone(result['TraceId'])
        self.assertIsInstance(result['RemoteTraceId'], str)
        self.assertIsNone(result['ErrorMessage'])
        self.assertIsInstance(result['Message'], str)
        self.assertIsInstance(result['RootAccountObj'], dict)
        self.assertFalse(result['IsError'])

    def test_register_root_account_fail_to_create_root_account_table_01(self):
        self.configuration.persistence_configuration = PersistenceConfiguration(
            persistence_path=tempfile.gettempdir(),
            persistence_file='accounts',
            flags={
                'PersistPassphrase': True,
                'PersistOnSuccess': True,
            },
            functions={
                'CreateDatabaseTable': Mock(side_effect=Exception('CreateDatabaseTable unavailable')),
                'CreateRootAccountTable': MagicMock(return_value=False),
                'CreateRootAccount': Mock(side_effect=Exception('CreateDatabaseTable unavailable')),
            }
        )
        with self.assertRaises(Exception):
            root_account_registration(
                email_address='test@example.tld',
                passphrase='111 abcdefghijklm 222 *',
                account_name='unittest',
                configuration=self.configuration,
                trace_id=None
            )

    def test_register_root_account_remote_service_error_01(self):
        comms_response = CommsResponse(
            is_error=False,
            response_code=1,
            response_code_description=None,
            response_data=json.dumps(
                {
                    'Data': None,
                    'ErrorMessage': 'Some error occurred',
                    'IsError': True,
                    'Message': None,
                    'TraceId': '1111-2222-3333-4444'
                }
            ),
            trace_id=None
        )
        self.configuration.comms_configurations = CommsConfiguration(
            service_handlers={
                'GetServiceUri': MagicMock(return_value='http://localhost/'),
                'Get': None,
                'JsonPost': MagicMock(return_value=comms_response),
            },
            service_region='us1'
        )
        result = root_account_registration(
            email_address='test@example.tld',
            passphrase='111 abcdefghijklm 222 *',
            account_name='unittest',
            configuration=self.configuration,
            trace_id=None
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('IsError' in result)
        self.assertTrue('TraceId' in result)
        self.assertTrue('RemoteTraceId' in result)
        self.assertTrue('ErrorMessage' in result)
        self.assertTrue('Message' in result)
        self.assertTrue('RootAccountObj' in result)
        self.assertIsInstance(result['IsError'], bool)
        self.assertIsNone(result['TraceId'])
        self.assertIsInstance(result['RemoteTraceId'], str)
        self.assertIsNotNone(result['ErrorMessage'])
        self.assertIsInstance(result['ErrorMessage'], str)
        self.assertIsNone(result['Message'])
        self.assertIsNone(result['RootAccountObj'])
        self.assertTrue(result['IsError'])

    def test_register_root_account_invalid_response_dict_causing_exception_01(self):
        comms_response = CommsResponse(
            is_error=False,
            response_code=1,
            response_code_description=None,
            response_data='\n\t\0',
            trace_id=None
        )
        self.configuration.comms_configurations = CommsConfiguration(
            service_handlers={
                'GetServiceUri': MagicMock(return_value='http://localhost/'),
                'Get': None,
                'JsonPost': MagicMock(return_value=comms_response),
            },
            service_region='us1'
        )
        result = root_account_registration(
            email_address='test@example.tld',
            passphrase='111 abcdefghijklm 222 *',
            account_name='unittest',
            configuration=self.configuration,
            trace_id=None
        )
        self.assertIsNotNone(result)
        self.assertTrue(result['IsError'])
        self.assertTrue('EXCEPTION' in result['ErrorMessage'])


class TestPing(unittest.TestCase):

    def setUp(self):

        # Setup the test logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        ch = TestLogHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        test_logger = OculusDLogger(logger_impl=logger)

        positive_comms_response = CommsResponse(
            is_error=False,
            response_code=1,
            response_code_description=None,
            response_data=json.dumps({"Ping": "ok"}),
            trace_id=None
        )
        comms_configuration = CommsConfiguration(
            service_handlers={
                'GetServiceUri': MagicMock(return_value='http://localhost/'),
                'Get': MagicMock(return_value=positive_comms_response),
                'JsonPost': None,
            },
            service_region='us1'
        )
        persistence_configuration = PersistenceConfiguration(
            persistence_path=tempfile.gettempdir(),
            persistence_file='accounts',
            flags={
                'PersistPassphrase': True,
                'PersistOnSuccess': True,
            }
        )
        self.configuration = Configuration(
            persistence_configuration=persistence_configuration,
            comms_configurations=comms_configuration,
            logger=test_logger
        )
        if Path(self.configuration.persistence_configuration.persistence_full_path).is_file():
            os.remove(self.configuration.persistence_configuration.persistence_full_path)
        self.conn = None

    def test_ping_positive_01(self):
        result = check_service_response(configuration=self.configuration)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('IsError' in result)
        self.assertTrue('TraceId' in result)
        self.assertTrue('RemoteTraceId' in result)
        self.assertTrue('ErrorMessage' in result)
        self.assertTrue('Message' in result)
        self.assertTrue('PingResult' in result)
        self.assertIsInstance(result['IsError'], bool)
        self.assertIsNone(result['TraceId'])
        self.assertIsNone(result['RemoteTraceId'])
        self.assertIsNone(result['ErrorMessage'])
        self.assertIsInstance(result['Message'], str)
        self.assertIsInstance(result['PingResult'], dict)
        self.assertFalse(result['IsError'])

    def test_ping_invalid_return_data_causing_exception_01(self):
        comms_response = CommsResponse(
            is_error=False,
            response_code=1,
            response_code_description=None,
            response_data='\n\t\0',
            trace_id=None
        )
        self.configuration.comms_configurations = CommsConfiguration(
            service_handlers={
                'GetServiceUri': MagicMock(return_value='http://localhost/'),
                'Get': MagicMock(return_value=comms_response),
                'JsonPost': None,
            },
            service_region='us1'
        )
        result = check_service_response(configuration=self.configuration)
        self.assertIsNotNone(result)
        self.assertTrue(result['IsError'])
        self.assertTrue('EXCEPTION' in result['ErrorMessage'])


if __name__ == '__main__':
    unittest.main()

# EOF
