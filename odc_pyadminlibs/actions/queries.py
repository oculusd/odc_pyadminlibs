# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons import HOME, get_utc_timestamp
from odc_pycommons.comms import get, json_post, get_service_uri, SERVICE_URIS
from odc_pycommons.models import RootAccount, Thing, CommsRequest
import traceback
import os
import json


def _write_file(file_path: str, file_name: str, data: str)->bool:
    try:
        with open('{}{}{}'.format(file_path, os.sep, file_name), 'a') as f:
            f.write(data)
    except:
        print(traceback.format_exc())
        return False
    return True

def _persist_data_to_file(
    thing_name: str,
    sensor_name: str,
    data: dict,
    axis_names: list,
    file_path: str='.{}'.format(os.sep),
    separate_file_per_axis: bool=False
)->str:
    file_name = None
    thing_name = thing_name.replace(' ', '-')
    base_filename = '{}_{}_'.format(thing_name, get_utc_timestamp())
    if separate_file_per_axis is False:
        header_line = 'timestamp'
        for axis_name in axis_names:
            header_line = '{},{}'.format(header_line, axis_name)
        file_data = '{}\n'.format(header_line)
        for timestamp, ts_data in data.items():
            record = '{}'.format(timestamp)
            for axis_name in axis_names:
                axis_data_str = ''
                if ts_data[axis_name] is not None:
                    axis_data_str = '{}'.format(ts_data[axis_name])
                record = '{},{}'.format(record,axis_data_str)
            file_data = '{}{}\n'.format(file_data, record)

        file_name = '{}_all-sensors.csv'.format(base_filename)
        if _write_file(
            file_path=file_path,
            file_name=file_name,
            data=file_data
        ):
            return '{}{}{}'.format(file_path, os.sep, file_name)
        else:
            raise Exception('Failed to write data to file')
    else:
        file_names = list()
        for axis_name in axis_names:
            header_line = 'timestamp,{}'.format(axis_name)
            file_data = '{}\n'.format(header_line)
            for timestamp, ts_data in data.items():
                axis_data_str = ''
                if ts_data[axis_name] is not None:
                    axis_data_str = '{}'.format(ts_data[axis_name])
                record = 'timestamp,{}\n'.format(axis_data_str)
                file_data = '{}{}'.format(file_data, record)

            axis_file_name_part = axis_name.replace(' ', '-')
            file_name = '{}_sensor_{}.csv'.format(base_filename, axis_file_name_part)
            if _write_file(
                file_path=file_path,
                file_name=file_name,
                data=file_data
            ):
                file_names.append('{}{}{}'.format(file_path, os.sep, file_name))
            else:
                raise Exception('Failed to write data to file')
        return ', '.join(file_names)
    return file_name



def _get_all_timestamps(data: dict, axis_names: list)->dict:
    timestamps = dict()
    try:
        if len(axis_names) > 0:
            for axis_name, axis_data in data.items():
                for row in axis_data:
                    if row[0] not in timestamps:
                        timestamps[row[0]] = dict()
                        for axis_name in axis_names:
                            timestamps[row[0]][axis_name] = ''
    except:
        traceback.print_exc()
        timestamps = dict()
    return timestamps


def _generate_csv_data(data: dict)->dict:
    result = dict()
    result['CsvData'] = ''
    result['TimestampOrderedDataSet'] = dict()
    result['TotalRecordsReturned'] = 0
    csv_data = ''
    try:
        data_lines = list()
        if len(data) > 0:
            axis_names = list(data.keys())
            axis_names.sort()
            timestamp_ordered_dataset = _get_all_timestamps(data=data, axis_names=axis_names)
            result['TimestampOrderedDataSet'] = timestamp_ordered_dataset
            header = 'timestamp'
            for axis_name in axis_names:
                header = '{},"{}"'.format(header, axis_name)
            csv_data = header
            for axis_name, axis_data in data.items():
                for row in axis_data:
                    if row[0] in timestamp_ordered_dataset:
                        if axis_name in timestamp_ordered_dataset[row[0]]:
                            timestamp_ordered_dataset[row[0]][axis_name] = row[1]
            sorted_timestamps = list(timestamp_ordered_dataset.keys())
            sorted_timestamps.sort()
            for timestamp in sorted_timestamps:
                timestamp_row = timestamp_ordered_dataset[timestamp]
                line_entry = '{}'.format(timestamp)
                for axis_name in axis_names:
                    line_entry = '{},{}'.format(
                        line_entry,
                        timestamp_ordered_dataset[timestamp][axis_name]
                    )
                data_lines.append(line_entry)
        if len(data_lines) > 0:
            result['TotalRecordsReturned'] = len(data_lines)
            for line in data_lines:
                csv_data = '{}\n{}'.format(csv_data, line)
            csv_data = '{}\n'.format(csv_data)
            result['CsvData'] = csv_data
    except:
        traceback.print_exc()
        csv_data = None
    return result


def query_thing_sensor(
    root_account: RootAccount,
    thing: Thing,
    sensor_name: str,
    timestamp_start: int=(get_utc_timestamp()-(60*60*24)),
    timestamp_stop: int=(get_utc_timestamp()-300),
    timestamp_source: str='ORIGIN',
    limit: int=1440,
    axis_names: list=list(),
    persist_to_file: bool=False,
    file_path: str=None,
    separate_file_per_axis: bool=False,
    trace_id: str=None,
    service_region: str=None,
    return_data_set: bool=True
)->dict:
    result = dict()
    result['IsError'] = True
    result['TraceId'] = trace_id
    result['RemoteTraceId'] = None
    result['ErrorMessage'] = 'The remote service returned an unknown/undefined error'
    result['Message'] = None
    result['TotalRecordsReturned'] = 0
    result['CsvData'] = None
    result['PersistedFilename'] = None
    final_axis_names = list()
    final_axis_names_unmodified = list()
    thing_sensor_axis_names = list(thing.thing_sensors[sensor_name].sensor_axes.keys())
    if len(axis_names) == 0:
        for axis_name in thing_sensor_axis_names:
            final_axis_names.append(axis_name.replace(' ', '%20'))
            final_axis_names_unmodified.append(axis_name)
    else:
        for axis_name in axis_names:
            if axis_name in thing_sensor_axis_names:
                final_axis_names.append(axis_name.replace(' ', '%20'))
                final_axis_names_unmodified.append(axis_name)
    sensor_name = sensor_name.replace(' ', '%20')
    final_axis_names_as_string = ''
    for axis_name in thing_sensor_axis_names:
        final_axis_names_as_string = '{},{}'.format(final_axis_names_as_string, axis_name)
    final_axis_names_as_string = final_axis_names_as_string.replace(',', '', 1)
    uri = get_service_uri(
        service_name='RootAccountThingSensorQuery', 
        region=service_region
    ).lower().replace('<<user_token>>', root_account.root_account_session_token).replace('<<thing_token>>', thing.thing_token).replace('<<sensor_name>>', sensor_name)
    req_result = get(
        request=CommsRequest(
            uri=uri,
            trace_id=trace_id
        ),
        user_agent=None,
        uri_parameters={
            'time_source': timestamp_source,
            'start': timestamp_start,
            'stop': timestamp_stop,
            'limit': limit,
            'axes_requested': final_axis_names_as_string,
        }
    )
    if req_result.is_error is False:
            if req_result.response_data is not None:
                try:
                    response_dict = json.loads(req_result.response_data)
                    if 'IsError' in response_dict:
                        if response_dict['IsError'] is False:
                            if 'Data' in response_dict:
                                result['Message'] = 'Number of records captured: {}'.format(len(response_dict['Data']))
                                generated_csv_data_dict = _generate_csv_data(data=response_dict['Data'])
                                result['TotalRecordsReturned'] = generated_csv_data_dict['TotalRecordsReturned']
                                if return_data_set:
                                    result['CsvData']  = generated_csv_data_dict['CsvData']
                                if persist_to_file:
                                    file_name = _persist_data_to_file(
                                        thing_name=thing.thing_name,
                                        sensor_name=sensor_name,
                                        file_path=file_path,
                                        data=generated_csv_data_dict['TimestampOrderedDataSet'],
                                        separate_file_per_axis=separate_file_per_axis,
                                        axis_names=final_axis_names_unmodified
                                    )
                                    result['PersistedFilename'] = file_name
                                result['IsError'] = False
                                result['ErrorMessage'] = None
                            else:
                                result['ErrorMessage'] = 'No returned data found'
                        else:
                            result['ErrorMessage'] = response_dict['ErrorMessage']
                except:
                    result['ErrorMessage'] = 'EXCEPTION: {}'.format(traceback.format_exc())
    return result


# EOF
