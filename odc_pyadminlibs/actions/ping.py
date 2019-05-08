# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons.models import CommsRequest, CommsResponse
from odc_pycommons import get_utc_timestamp
from odc_pyadminlibs import Configuration
import traceback
from datetime import datetime
import os
import json


def check_service_response(
    configuration: Configuration=Configuration(),
    trace_id: str=None
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = result['Message'] = 'Remote service for region "{}" is down'.format(configuration.comms_configurations.service_region)
    result['PingResult'] = dict()
    result['PingResult']['ServiceUp'] = False
    result['PingResult']['ResponseTime'] = 0
    result['PingResult']['Response'] = None
    request = CommsRequest(
        uri=configuration.comms_configurations.get_service_uri(
            service_name='Ping',
            region=configuration.comms_configurations.service_region
        ),
        trace_id=trace_id
    )
    now = get_utc_timestamp(with_decimal=True)
    req_result = configuration.comms_configurations.get(request=request)
    if req_result.is_error is False:
        if req_result.response_data is not None:
            try:
                result['PingResult']['Response'] = json.loads(req_result.response_data)
                if 'Ping' in result['PingResult']['Response']:
                    if result['PingResult']['Response']['Ping'].lower() == 'ok':
                        result['IsError'] = False
                        result['ErrorMessage'] = None
                        result['Message'] = 'Remote service for region "{}" is up'.format(configuration.comms_configurations.service_region)
                        result['PingResult']['ServiceUp'] = True
            except:
                result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    result['PingResult']['ResponseTime'] = get_utc_timestamp(with_decimal=True) - now
    return result



# EOF
