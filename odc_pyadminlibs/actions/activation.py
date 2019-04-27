# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons import HOME
from odc_pycommons.comms import json_post, get_service_uri, SERVICE_URIS
from odc_pycommons.models import RootAccount, CommsRestFulRequest, CommsResponse, Sensor, SensorAxis, SensorAxisReading, Thing
from odc_pycommons.models import RootAccount, CommsRestFulRequest, CommsResponse
from odc_pyadminlibs.persistence.root_account_persistence import read_root_account_by_root_account_ref
import traceback
import os
import json


def activate_root_account(
    root_account: RootAccount,
    activation_token: str,
    service_region: str=None,
    trace_id: str=None
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    uri = get_service_uri(service_name='RootAccountActivation', region=service_region).lower().replace('<<root_account_id>>', root_account.root_account_ref)
    req_result = json_post(
        request=CommsRestFulRequest(
            uri=uri,
            data={
                'ActivationToken': activation_token,
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
                    else:
                        result['ErrorMessage'] = response_dict['ErrorMessage']
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    return result

# EOF
