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


D=Decimal


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

# EOF
