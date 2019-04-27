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


D = Decimal


def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return D(s)


# Register the adapter
sqlite3.register_adapter(D, adapt_decimal)

# Register the converter
sqlite3.register_converter("decimal", convert_decimal)


def sql_get_connection(data_path: str, data_file: str, L: OculusDLogger=OculusDLogger()):
    """This function will create the root account table in the database.

    :param data_path: containing the path to the database file
    :type data_path: str
    :param data_file: contiaing the filename of the database
    :type data_file: str
    :param L: logger class, from odc_pycommons
    :type L: OculusDLogger

    :returns: sqlite3.Connection -- A sqlite connection

    :raises: Exception
    """
    try:
        db_file = '{}{}{}'.format(data_path, os.sep, data_file)
        L.info(message='Connecting to "{}"'.format(db_file))
        conn = sqlite3.connect(db_file, isolation_level=None)
        conn.execute('pragma journal_mode=wal')
        return conn
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    raise Exception('Unable to obtain DB connection')


def create_database_table(
    database_table_name: str,
    database_table_definition: str,
    persistence_file: str,
    persistence_path: str=HOME,
    L: OculusDLogger=OculusDLogger()
):
    """This function will create a table in the database.

    Example: 

    >>> from odc_pyadminlibs.persistence import create_database_table
    >>> create_database_table(database_table_name='my_test_table', database_table_definition='some_id integer primary key, some_name text', persistence_file='my_test.db')
    2019-04-27 09:58:45,840 - INFO - Connecting to "C:\\Users\\auser\\.oculusd\\my_test.db"

    :param database_table_name: The nbame of the table
    :type database_table_name: str
    :param database_table_definition: The table columns and types
    :type database_table_definition: str
    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str
    :param L: logger class, from odc_pycommons
    :type L: OculusDLogger

    :returns: sqlite3.Connection -- A sqlite connection

    :raises: Exception
    """
    result = False
    connected = False
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file, L=L)
        connected = True
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(database_table_name, database_table_definition))
        conn.commit()
        conn.close()
        connected = False
        result = True
        L.info(message='Created table "{}"'.format(database_table_name))
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    if connected:
        try:
            conn.commit()
            conn.close()
        except:                                                                         # pragma: no cover
            pass                                                                        # pragma: no cover
    if os.path.isfile(db_file) is False:                                                # pragma: no cover
        raise Exception('Failed to create database - no database file was created')     # pragma: no cover
    if result is False:
        raise Exception('Failed to create database')

# EOF
