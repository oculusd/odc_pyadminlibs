# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

import os
from odc_pycommons import HOME, OculusDLogger
from odc_pycommons.comms import json_post, get_service_uri, get
from odc_pyadminlibs.persistence import create_database_table
from odc_pyadminlibs.persistence.root_account_persistence import create_root_account, create_root_account_table


class PersistenceConfiguration:

    def __init__(
        self,
        persistence_path: str=HOME,
        persistence_file: str='accounts',
        functions: dict={
            'CreateDatabaseTable': create_database_table,
            'CreateRootAccountTable': create_root_account_table,
            'CreateRootAccount': create_root_account,
        },
        flags: dict={
            'PersistPassphrase': False,
            'PersistOnSuccess': True,
        }
    ):
        self.persistence_path = persistence_path
        self.persistence_file = persistence_file
        self.persistence_full_path = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
        self.flags = flags
        self.create_database_table = create_database_table
        if 'CreateDatabaseTable' in functions:
            self.create_database_table = functions['CreateDatabaseTable']
        self.create_root_account_table = create_root_account_table
        if 'CreateRootAccountTable' in functions:
            self.create_root_account_table = functions['CreateRootAccountTable']
        self.create_root_account = create_root_account
        if 'CreateRootAccount' in functions:
            self.create_root_account = functions['CreateRootAccount']


class CommsConfiguration:

    def __init__(
        self,
        service_handlers: dict={
            'GetServiceUri': get_service_uri,
            'Get': get,
            'JsonPost': json_post,
        },
        service_region: str=None
    ):
        self.get_service_uri = get_service_uri
        if 'GetServiceUri' in service_handlers:
            self.get_service_uri = service_handlers['GetServiceUri']
        self.get = get
        if 'Get' in service_handlers:
            self.get = service_handlers['Get']
        self.json_post = json_post
        if 'JsonPost' in service_handlers:
            self.json_post = service_handlers['JsonPost']
        self.service_region = service_region


class Configuration:

    def __init__(
        self,
        persistence_configuration: PersistenceConfiguration=PersistenceConfiguration(),
        comms_configurations: CommsConfiguration=CommsConfiguration(),
        logger: OculusDLogger=OculusDLogger()
    ):
        self.persistence_configuration = persistence_configuration
        self.logger = logger
        self.comms_configurations = comms_configurations


# EOF
