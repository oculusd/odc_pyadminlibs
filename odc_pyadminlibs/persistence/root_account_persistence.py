# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pyadminlibs.persistence import sql_get_connection, create_database_table
from odc_pycommons import HOME, OculusDLogger
import os
import traceback


L = OculusDLogger()


def create_root_account_table(
    persistence_path: str=HOME,
    persistence_file: str='accounts'
)->bool:
    """This function will create the root account table in the database.

    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str

    :returns: bool -- the result: True if successful 
    """
    conn = None
    connected = False
    table_created = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        create_database_table(
            database_table_name='root_account',
            database_table_definition='root_account_id TEXT PRIMARY KEY, root_account_data TEXT',
            persistence_file=persistence_file,
            persistence_path=persistence_path
        )
        conn.commit()
        conn.close()
        connected = False
        table_created = True
        L.info(message='Created table root account table')
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    return table_created


def create_root_account(
    root_account_id: str,
    root_account: str,
    persistence_path: str=HOME,
    persistence_file: str='accounts'
)->bool:
    """This function will persist a new root account into the database.

    :param root_account_id: :containing the root account ID
    :type root_account_id: str
    :param root_account: Any string representation (usually JSON) representing the root account
    :type root_account: str
    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str

    :returns: bool -- the result: True if successful 
    """
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'INSERT INTO root_account (root_account_id, root_account_data) VALUES (?, ?)',
            (
                root_account_id,
                root_account
            )
        )
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
    return False


def read_root_account_by_root_account_ref(
    root_account_id: str,
    persistence_path: str=HOME,
    persistence_file: str='accounts'
)->str:
    """This function will load a root account from the database.

    :param root_account_id: :containing the root account ID
    :type root_account_id: str
    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str

    :returns: str -- contains the data read from the database, typically JSON data

    :raises: Exception 
    """
    conn = None
    connected = False
    ra = None
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'SELECT root_account_data FROM root_account WHERE root_account_id = ?', 
            (
                root_account_id, 
            )
        )
        row = c.fetchone()
        ra = '{}'.format(row[0])
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
    if ra is not None:
        return ra
    raise Exception('Root account for not loaded')


def update_root_account(
    root_account_id: str,
    root_account: str,
    persistence_path: str=HOME,
    persistence_file: str='accounts'
)->bool:
    """This function will update a root account in the database.

    :param root_account_id: :containing the root account ID
    :type root_account_id: str
    :param root_account: Any string representation (usually JSON) representing the root account
    :type root_account: str
    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str

    :returns: bool -- the result: True if successful
    """
    conn = None
    connected = False
    success = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'UPDATE root_account SET root_account_data = ? WHERE root_account_id = ?', 
            (
                root_account, 
                root_account_id, 
            )
        )
        conn.commit()
        conn.close()
        connected = False
        success = True
    except:
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
    if connected:
        try:
            conn.commit()
            conn.close()
        except:
            pass
    return success


def get_root_account_ids(
    persistence_path: str=HOME,
    persistence_file: str='accounts'
)->list:
    """This function will return a list of root account ID's from the database.

    :param persistence_path: containing the path to the database file
    :type persistence_path: str
    :param persistence_file: contiaing the filename of the database
    :type persistence_file: str

    :returns: list -- the list of root account ID's
    """
    conn = None
    connected = False
    ids = list()
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        for row in  c.execute('SELECT root_account_id FROM root_account'):
            ids.append('{}'.format(row[0]))
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
    return ids



# EOF
