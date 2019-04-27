# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pyadminlibs.persistence import sql_get_connection
from odc_pycommons.models import RootAccount, Thing, Sensor, SensorAxis
import os
import traceback
import json


def create_thing(
    thing: Thing,
    linked_root_account_id: str,
    persistence_path: str,
    persistence_file: str
)->bool:
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS thing_definition (thing_id TEXT NOT NULL PRIMARY KEY, linked_root_account_id TEXT NOT NULL, thing_name TEXT NOT NULL, thing_description TEXT, thing_meta_data TEXT, thing_token TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS sensor_definition (sensor_name TEXT NOT NULL, linked_thing_id TEXT NOT NULL, sensor_description TEXT, PRIMARY KEY (sensor_name, linked_thing_id))')
        c.execute('CREATE TABLE IF NOT EXISTS sensor_axis_definition (sensor_name TEXT NOT NULL, linked_thing_id TEXT NOT NULL, sensor_axis_name TEXT, axis_user_defined_type TEXT, axis_data_type TEXT, PRIMARY KEY (sensor_name, linked_thing_id, sensor_axis_name))')
        conn.commit()
        c.execute(
            'INSERT INTO thing_definition (thing_id, linked_root_account_id, thing_name, thing_description, thing_meta_data) VALUES (?, ?, ?, ?, ?)',
            (
                thing.thing_id,
                linked_root_account_id,
                thing.thing_name,
                thing.thing_description,
                json.dumps(thing.thing_meta_data),
            )
        )
        for sensor_name, sensor in thing.thing_sensors.items():
            c.execute(
                'INSERT INTO sensor_definition (sensor_name, linked_thing_id, sensor_description) VALUES (?, ?, ?)',
                (
                    sensor.sensor_name,
                    thing.thing_id,
                    sensor.sensor_description,
                )
            )
            for sensor_axis_name, sensor_axis in sensor.sensor_axes.items():
                c.execute(
                    'INSERT INTO sensor_axis_definition (sensor_name, linked_thing_id, sensor_axis_name, axis_user_defined_type, axis_data_type) VALUES (?, ?, ?, ?, ?)',
                    (
                        sensor.sensor_name,
                        thing.thing_id,
                        sensor_axis.axis_name,
                        sensor_axis.axis_user_defined_type,
                        sensor_axis.axis_data_type,
                    )
                )
        conn.commit()
        conn.close()
        connected = False
    except:
        traceback.print_exc()
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    if os.path.isfile(db_file):
        return True
    return False


def read_thing_from_thing_id(
    thing_id: str,
    persistence_path: str,
    persistence_file: str
)->Thing:
    thing = None
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'SELECT linked_root_account_id,thing_name,thing_description,thing_meta_data,thing_token FROM thing_definition WHERE thing_id = ?', 
            (
                thing_id,
            )
        )
        row = c.fetchone()
        thing = Thing(
            thing_name=row[1],
            thing_description=row[2],
            thing_meta_data=json.loads(row[3]),
            thing_id=thing_id,
            thing_token=row[4]
        )
        for row in c.execute(
            'SELECT sensor_name, sensor_description FROM sensor_definition WHERE linked_thing_id = ?',
            (
                thing_id,
            )
        ):
            sensor = Sensor(
                sensor_name=row[0],
                sensor_description=row[1]
            )
            for sa_row in c.execute(
                'SELECT sensor_axis_name,axis_user_defined_type,axis_data_type FROM sensor_axis_definition WHERE linked_thing_id = ? AND sensor_name = ?',
                (
                    thing_id,
                    sensor.sensor_name,
                )
            ):
                sensor_axis = SensorAxis(
                    axis_name=sa_row[0],
                    axis_user_defined_type=sa_row[1],
                    axis_data_type=sa_row[2]
                )
                sensor.add_sensor_axis(sensor_axis=sensor_axis)
            thing.add_sensor(sensor=sensor)
        conn.commit()
        conn.close()
        connected = False
    except:
        traceback.print_exc()
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    return thing


def read_all_things_for_linked_root_account_id(
    linked_root_account_id: str,
    persistence_path: str,
    persistence_file: str
)->dict:
    things = dict()
    thing_ids = list()
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        for row in c.execute(
            'SELECT thing_id FROM thing_definition WHERE linked_root_account_id = ?',
            (
                linked_root_account_id,
            )
        ):
            thing_ids.append(row[0])
        conn.commit()
        conn.close()
        connected = False
    except:
        traceback.print_exc()
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    for thing_id in thing_ids:
        thing = read_thing_from_thing_id(thing_id=thing_id, persistence_path=persistence_path, persistence_file=persistence_file)
        if thing is not None:
            if isinstance(thing, Thing):
                things[thing.thing_id] = thing
    return things


def update_thing_token(
    thing: Thing,
    persistence_path: str,
    persistence_file: str
)->bool:
    conn = None
    connected = False
    result = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'UPDATE thing_definition SET thing_token = ? WHERE thing_id = ?',
            (
                thing.thing_token,
                thing.thing_id
            )
        )
        conn.commit()
        conn.close()
        connected = False
        result = True
    except:
        traceback.print_exc()
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    return result

# EOF
