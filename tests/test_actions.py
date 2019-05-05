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
import logging
from odc_pycommons import OculusDLogger, DEBUG, formatter, get_utc_timestamp
from odc_pycommons.models import CommsResponse
#from odc_pycommons.comms import json_post, get_service_uri
from pathlib import Path
import os
import traceback
import time
import tempfile
from decimal import Decimal
import json
from odc_pyadminlibs.actions.register import root_account_registration


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
json_post = MagicMock(return_value=positive_comms_response)
get_service_uri = MagicMock(return_value='http://localhost/')
DB_TEST_DIR = tempfile.gettempdir()


class TestLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.lines = list()

    def emit(self, record):
        self.lines.append(self.format(record))

    def flush(self):
        self.lines = list()


class TestRegisterRootAccount(unittest.TestCase):

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

    def test_register_root_account_positive_01(self):
        """This test aims to verify the return data structure of a guarenteed positive result.
        """
        result = root_account_registration(
            email_address='test@example.tld',
            passphrase='111 abcdefghijklm 222 *',
            account_name='unittest',
            persist_on_success=False,
            persistence_path=None,
            persistence_file=None,
            persist_with_passphrase=False,
            service_region=None,
            trace_id=None,
            L=self.test_logger,
            remote_request_function=json_post
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
        #self.assertTrue('')



if __name__ == '__main__':
    unittest.main()

# EOF
