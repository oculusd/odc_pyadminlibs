# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

from odc_pyadminlibs.persistence import sql_get_connection
from odc_pycommons.models import RootAccount
import os
import traceback


def create_root_account(
    root_account: RootAccount,
    persistence_path: str,
    persistence_file: str,
    persist_with_passphrase: bool=False,
)->bool:
    db_file = '{}{}{}'.format(persistence_path, os.sep, persistence_file)
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS root_account (root_account_id TEXT PRIMARY KEY, email_address TEXT, account_name TEXT, passphrase TEXT, root_session TEXT, root_session_create_timestamp INTEGER)')
        conn.commit()
        if persist_with_passphrase is False:
            passphrase  = None
        else:
            passphrase = root_account.passphrase
        c.execute(
            'INSERT INTO root_account (root_account_id, email_address, account_name, passphrase, root_session, root_session_create_timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            (
                root_account.root_account_ref,
                root_account.email_address,
                root_account.account_name,
                passphrase,
                root_account.root_account_session_token,
                root_account.root_account_session_create_timestamp
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


def read_root_account_by_email_address(
    email_address: str,
    persistence_path: str,
    persistence_file: str
)->RootAccount:
    conn = None
    connected = False
    ra = None
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute('SELECT root_account_id,account_name,passphrase,root_session,root_session_create_timestamp FROM root_account WHERE email_address=?', (email_address, ))
        row = c.fetchone()
        ra = RootAccount(
            email_address=email_address,
            passphrase=row[2],
            account_name=row[1],
            passphrase_is_insecure=True,
            secure_passphrase=False
        )
        ra.set_root_account_ref(root_account_ref=row[0])
        if row[3] is not None:
            ra.set_root_account_session_token(root_account_session_token=row[3])
            ra.root_account_session_create_timestamp = row[4]
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
    if ra is not None:
        return ra
    raise Exception('Root account for "{}" not loaded'.format(email_address))


def read_root_account_by_root_account_ref(
    root_account_ref: str,
    persistence_path: str,
    persistence_file: str
)->RootAccount:
    conn = None
    connected = False
    ra = None
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'SELECT email_address,account_name,passphrase,root_session,root_session_create_timestamp FROM root_account WHERE root_account_id = ?', 
            (
                root_account_ref, 
            )
        )
        row = c.fetchone()
        ra = RootAccount(
            email_address=row[0],
            passphrase=row[2],
            account_name=row[1],
            passphrase_is_insecure=True,
            secure_passphrase=False
        )
        ra.set_root_account_ref(root_account_ref=root_account_ref)
        if row[3] is not None:
            ra.set_root_account_session_token(root_account_session_token=row[3])
            ra.root_account_session_create_timestamp = row[4]
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
    if ra is not None:
        return ra
    raise Exception('Root account for "{}" not loaded'.format(root_account_ref))


def read_root_accounts_summary(
    persistence_path: str,
    persistence_file: str
)->list:
    root_accounts = list()
    conn = None
    connected = False
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        for row in c.execute('SELECT root_account_id FROM root_account'):
            root_accounts.append(
                read_root_account_by_root_account_ref(
                    root_account_ref=row[0],
                    persistence_path=persistence_path,
                    persistence_file=persistence_file
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
    return root_accounts


def update_root_account_set_passphrase(
    root_account_ref: str,
    persistence_path: str,
    persistence_file: str,
    passphrase: str=None
)->RootAccount:
    conn = None
    connected = False
    ra = None
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'UPDATE root_account SET passphrase = ?, root_session = ?, root_session_create_timestamp = ? WHERE root_account_id=?', 
            (
                passphrase, 
                None,
                None,
                root_account_ref, 
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
    ra = read_root_account_by_root_account_ref(
        root_account_ref=root_account_ref,
        persistence_path=persistence_path,
        persistence_file=persistence_file
    )
    if ra is not None:
        return ra
    raise Exception('Root account for "{}" not loaded'.format(root_account_ref))


def update_root_account_set_session(
    root_account: RootAccount,
    persistence_path: str,
    persistence_file: str,
)->RootAccount:
    conn = None
    connected = False
    ra = None
    try:
        conn = sql_get_connection(data_path=persistence_path, data_file=persistence_file)
        connected = True
        c = conn.cursor()
        c.execute(
            'UPDATE root_account SET root_session=?, root_session_create_timestamp=? WHERE root_account_id=?', 
            (
                root_account.root_account_session_token, 
                root_account.root_account_session_create_timestamp, 
                root_account.root_account_ref,
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
    ra = read_root_account_by_root_account_ref(
        root_account_ref=root_account.root_account_ref,
        persistence_path=persistence_path,
        persistence_file=persistence_file
    )
    if ra is not None:
        return ra
    raise Exception('Root account for "{}" not loaded'.format(root_account.root_account_ref))



# EOF
