# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons import HOME, get_utc_timestamp
from odc_pycommons.comms import get, get_service_uri, SERVICE_URIS
from odc_pycommons.models import CommsRequest, CommsResponse
import traceback
from datetime import datetime
import os
import json


def check_service_response(
    service_region: str=None,
    trace_id: str=None
)->dict:
    result = dict()
    result['ServiceUp'] = False
    result['ResponseTime'] = 0
    result['Response'] = None
    request = CommsRequest(
        uri=get_service_uri(service_name='Ping', region=service_region),
        trace_id=trace_id
    )
    now = get_utc_timestamp(with_decimal=True)
    req_result = get(request=request)
    if req_result.is_error is False:
        if req_result.response_data is not None:
            try:
                result['Response'] = json.loads(req_result.response_data)
                if 'Ping' in result['Response']:
                    if result['Response']['Ping'].lower() == 'ok':
                        result['ServiceUp'] = True
            except:
                result['Response'] = 'EXCEPTION during JSON Conversion. Original data: {}\n\nEXCEPTION: {}'.format(
                    req_result.response_data,
                    traceback.format_exc()
                )
    result['ResponseTime'] = get_utc_timestamp(with_decimal=True) - now
    return result



# EOF
