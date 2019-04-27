# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
NOTE: Refer to https://stackoverflow.com/questions/6319409/how-to-convert-python-decimal-to-sqlite-numeric for dealing with Decimal conversion
"""
import sqlite3
import traceback
from pathlib import Path
from decimal import Decimal
import os
from odc_pycommons import HOME, OculusDLogger


L = OculusDLogger()
D = Decimal


def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return D(s)


# Register the adapter
sqlite3.register_adapter(D, adapt_decimal)

# Register the converter
sqlite3.register_converter("decimal", convert_decimal)


def sql_get_connection(data_path: str, data_file: str):
    try:
        db_file = '{}{}{}'.format(data_path, os.sep, data_file)
        conn = sqlite3.connect(db_file, isolation_level=None)
        conn.execute('pragma journal_mode=wal')
        return conn
    except:
        traceback.print_exc()
    raise Exception('Unable to obtain DB connection')


def create_database_table(
    database_table_name: str,
    database_table_definition: str,
    persistence_file: str,
    persistence_path: str=HOME,
):
    result = False
    connected = False
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(database_table_name, database_table_definition))
        conn.commit()
        conn.close()
        connected = False
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    if os.path.isfile(db_file) is False:
        raise Exception('Failed to create database - no database file was created')
    if result is False:
        raise Exception('Failed to create database')

# EOF
