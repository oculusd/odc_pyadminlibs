# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

from odc_pycommons import HOME
from odc_pycommons.comms import get, json_post, get_service_uri, SERVICE_URIS
from odc_pycommons.models import RootAccount, Thing, CommsRestFulRequest, CommsResponse
import traceback
import os
import json
from datetime import datetime


def _create_sensor_axis_data_list(thing: Thing)->list:
    sensor_axis_data_list = list()
    for sensor_name, sensor in thing.thing_sensors.items():
        axis_readings = list()
        for sensor_axis_name, sensor_axis in sensor.sensor_axes.items():
            if len(sensor_axis.readings) > 0:
                for sensor_axis_reading in sensor_axis.readings:
                    axis_readings.append(
                        {
                            'AxisName': sensor_axis_name,
                            'Data': sensor_axis_reading.reading_value,
                        }
                    )
        if len(axis_readings) > 0:
            sensor_axis_data_list.append(
                {
                    'SensorName': sensor_name,
                    'AxisReadings': axis_readings,
                }
            )
    return sensor_axis_data_list


def log_data_with_root_account(
    root_account: RootAccount,
    thing: Thing,
    reading_timestamp: str='{}'.format(int(datetime.utcnow().timestamp())),
    service_region: str=None,
    trace_id: str=None
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['RecordsCaptured'] = 0
    uri = get_service_uri(
        service_name='LogSingleThing', 
        region=service_region
    ).lower().replace('<<user_token>>', root_account.root_account_session_token).replace('<<thing_token>>', thing.thing_token)
    sensor_data_set = _create_sensor_axis_data_list(thing=thing)
    if len(sensor_data_set) > 0:
        req_result = json_post(
            request=CommsRestFulRequest(
                uri=uri,
                data={
                    'ReadingTimestamp': reading_timestamp,
                    'Sensors': sensor_data_set,
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
                            if 'Data' in response_dict:
                                result['Message'] = 'Number of records captured: {}'.format(response_dict['Data'])
                                result['RecordsCaptured'] = response_dict['Data']
                        else:
                            result['ErrorMessage'] = response_dict['ErrorMessage']
                except:
                    result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    else:
        result['ErrorMessage'] = 'API call not made as sensor axis data set is empty (no sensor readings found)'
    return result


# EOF
