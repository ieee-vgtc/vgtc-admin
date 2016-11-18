# This is code adapted from
#   https://developers.google.com/admin-sdk/directory/v1/quickstart/python

from __future__ import print_function
import httplib2
import os
from data import *
import time
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googlestuff import *

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user https://www.googleapis.com/auth/admin.directory.group https://www.googleapis.com/auth/apps.groups.settings'
CLIENT_SECRET_FILE = '.credentials/client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join('.', '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'vgtc-admin.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_all_groups():
    gc = get_spreadsheet("VIS2016_roster_clean")
    roles =  load_sheet_by_name(gc, "Roles").get_all_records()
    admin = get_admin()
    groups = admin.groups()
    for role in roles:
        if role["Address"] <> '' and role["Address"] <> 'web@ieeevis.org':
            print(call_google(groups.insert(
                body={"email": role["Address"],
                      "description": role["RoleName"],
                      "name": role["RoleName"]})))

def call_google(call):
    try:
        result = call.execute()
    except Exception, e:
        print(e)
        raise e
    finally:
        time.sleep(1)
    return result

def get_admin():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)
    return service

def get_groupssettings():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('groupssettings', 'v1', http=http)
    return service

def create_group(email, description, name):
    admin = get_admin()
    g = admin.groups()
    call_google(g.insert(body={"email": email, "description": description, "name": name}))

def add_to_group(group_email, group_members):
    admin = get_admin()
    m = admin.members()
    if type(group_members) == type(''):
        group_members = [group_members]
    for name in group_members:
        call_google(m.insert(groupKey=group_email, body={"email": name, "role": 'MEMBER'}))

def remove_from_group(group_email, group_members):
    admin = get_admin()
    m = admin.members()
    if type(group_members) == type(''):
        group_members = [group_members]
    for name in group_members:
        call_google(m.delete(groupKey=group_email, memberKey=name))

def list_group(email):
    admin = get_admin()
    m = admin.members()
    result = call_google(m.list(groupKey=email))
    return set(l['email'] for l in result['members'])
