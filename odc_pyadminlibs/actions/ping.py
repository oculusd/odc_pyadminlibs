# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

from odc_pycommons import HOME
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
    now = datetime.utcnow().timestamp()
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
    result['ResponseTime'] = datetime.utcnow().timestamp() - now
    return result



# EOF
