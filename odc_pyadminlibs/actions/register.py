# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons import HOME, OculusDLogger
from odc_pycommons.comms import json_post, get_service_uri
from odc_pycommons.models import CommsRequest, CommsResponse, CommsRestFulRequest
from odc_pyadminlibs.persistence import create_database_table
from odc_pyadminlibs.persistence.root_account_persistence import create_root_account, create_root_account_table
import traceback
import os
import json


def root_account_registration(
    email_address: str,
    passphrase: str,
    account_name: str,
    persist_on_success: bool=True,
    persistence_path: str=HOME,
    persistence_file: str='accounts',
    persist_with_passphrase: bool=False,
    service_region: str=None,
    trace_id: str=None,
    L: OculusDLogger=OculusDLogger(),
    remote_request_function: object=json_post
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['RootAccountObj'] = None

    if persist_on_success  is True:
        if create_root_account_table(persistence_path=persistence_path, persistence_file=persistence_file, L=L) is False:
            result['ErrorMessage'] = 'Failed to create persistence store. Registration call to remote service was NOT made'
            L.error(message='Failed to create root_account persistence')
            raise Exception('Failed to create root_account persistence. This action cannot continue')

    request_data = {
        'AccountName': account_name,
        'PassPhrase': passphrase,
    }
    request = CommsRestFulRequest(
        uri=get_service_uri(service_name='RegisterRootAccount', region=service_region),
        data=request_data,
        trace_id=trace_id
    )
    req_result = remote_request_function(request=request, path_parameters={'emailAddress': email_address})
    if req_result.is_error is False:
        if req_result.response_data is not None:
            try:
                response_dict = json.loads(req_result.response_data)
                result['RemoteTraceId'] = response_dict['TraceId']
                result['Message'] = response_dict['Message']
                if 'IsError' in response_dict:
                    if response_dict['IsError'] is False:
                        result['RootAccountObj'] = dict()
                        result['RootAccountObj']['LastKnownStatus'] = response_dict['Data']['RootAccountStatus']
                        result['RootAccountObj']['RootAccountUser'] = dict()
                        result['RootAccountObj']['RootAccountUser']['EmailAddress'] = email_address
                        result['RootAccountObj']['RootAccountUser']['Passphrase'] = None
                        if persist_with_passphrase is True:
                            result['RootAccountObj']['RootAccountUser']['Passphrase'] = passphrase
                        result['IsError'] = False
                        result['ErrorMessage'] = None
                        if 'RootAccountId' in response_dict['Data']:
                            if persist_on_success:                                
                                create_root_account(
                                    root_account_id=response_dict['Data']['RootAccountId'],
                                    root_account=json.dumps(result['RootAccountObj']),
                                    persistence_path=persistence_path,
                                    persistence_file=persistence_file,
                                    L=L
                                )
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    return result
    

"""
def thing_registration(
    root_account: RootAccount,
    thing: Thing,
    persist_on_success: bool=True,
    persistence_path: str=HOME,
    persistence_file: str='things',
    service_region: str=None,
    trace_id: str=None
)->dict:
    if root_account.root_account_session_token is None:
        raise Exception('No authentication token present in root_account')
    result = dict()
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['Thing'] = thing
    uri = get_service_uri(service_name='RegisterThing', region=service_region).lower().replace('<<token>>', root_account.root_account_session_token)    
    req_result = json_post(
        request=CommsRestFulRequest(
            uri=uri,
            data=thing.to_dict(),
            trace_id=trace_id
        )
    )
    if req_result.is_error is False:
        if req_result.response_data is not None:
            try:
                response_dict = json.loads(req_result.response_data)
                result['RemoteTraceId'] = response_dict['TraceId']
                result['Message'] = response_dict['Message']
                if 'IsError' in response_dict:
                    if response_dict['IsError'] is False:
                        result['IsError'] = False
                        result['ErrorMessage'] = None
                        thing.thing_id = response_dict['Data']
                        result['Thing'] = thing
                        if persist_on_success:
                            if create_thing(
                                thing=thing,
                                linked_root_account_id=root_account.root_account_ref,
                                persistence_path=persistence_path,
                                persistence_file=persistence_file
                            ) is False:
                                result['ErrorMessage'] = 'Thing was created remotely but failed to persist locally' 
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    return result
"""


# EOF
