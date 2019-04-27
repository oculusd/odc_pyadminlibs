# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons import HOME
from odc_pycommons.comms import get, json_post, get_service_uri, SERVICE_URIS
from odc_pycommons.models import RootAccount, CommsRestFulRequest, CommsResponse, Thing, CommsRequest
from odc_pyadminlibs.persistence.root_account_persistence import update_root_account_set_session, update_root_account_set_passphrase
from odc_pyadminlibs.persistence.thing_persistence import update_thing_token
import traceback
import os
import json


def authenticate_root_account(
    root_account: RootAccount,
    service_region: str=None,
    persist_token: bool=False,
    persistence_path: str=HOME,
    persistence_file: str='root_account',
    trace_id: str=None
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['RootAccountObj'] = None
    req_result = json_post(
        request=CommsRestFulRequest(
            uri=get_service_uri(
                service_name='RootAccountAuthentication', 
                region=service_region
            ).lower().replace(
                '<<root_account_id>>',
                root_account.root_account_ref
            ),
            data={
                'EMailAddress': root_account.email_address,
                'PassPhrase': root_account.passphrase
            },
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
                        root_account.set_root_account_session_token(
                            root_account_session_token=response_dict['Data']
                        )
                        if persist_token is True:
                            update_root_account_set_session(
                                root_account=root_account,
                                persistence_path=persistence_path,
                                persistence_file=persistence_file
                            )
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    result['RootAccountObj'] = root_account
    return result


def get_thing_token_using_root_account(
    root_account: RootAccount,
    thing: Thing,
    service_region: str=None,
    persist_token: bool=True,
    persistence_path: str=HOME,
    persistence_file: str='things',
    user_agent: str=None,
    trace_id: str=None
)->dict:
    result = dict()
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['Thing'] = None
    req_result = get(
        request=CommsRequest(
            uri=get_service_uri(
                service_name='GetThingToken', 
                region=service_region
            ).lower().replace(
                '<<thing_id>>',
                thing.thing_id
            ).replace(
                '<<user_token>>',
                root_account.root_account_session_token
            ),
            trace_id=trace_id
        ),
        user_agent=user_agent
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
                        thing.thing_token = response_dict['Data']
                        if persist_token is True:
                            if update_thing_token(
                                thing=thing,
                                persistence_path=persistence_path,
                                persistence_file=persistence_file
                            ) is False:
                                result['ErrorMessage'] = 'Authentication successfull but token persistence failed. Token: {}'.format(thing.thing_token)
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    result['Thing'] = thing
    return result


def reset_root_account(
    root_account: RootAccount,
    service_region: str=None,
    persist_passphrase: bool=False,
    persistence_path: str=HOME,
    persistence_file: str='root_account',
    trace_id: str=None
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['RootAccountObj'] = root_account
    req_result = json_post(
        request=CommsRestFulRequest(
            uri=get_service_uri(
                service_name='RootAccountReset', 
                region=service_region
            ).lower().replace(
                '<<root_account_id>>',
                root_account.root_account_ref
            ),
            data={
                'Passphrase': root_account.passphrase
            },
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
                        if persist_passphrase is True:
                            update_root_account_set_passphrase(
                                root_account_ref=root_account.root_account_ref,
                                persistence_path=persistence_path,
                                persistence_file=persistence_file,
                                passphrase=root_account.passphrase
                            )
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    result['RootAccountObj'] = root_account
    return result

# EOF
