"""
A thin RDBMS-like layer on top of google spreadsheets.

Carlos Scheidegger and Sam Gratzl, 2016

We recommend you use this under a virtual environment. Create
a virtualenv and then install the required libraries with

$ pip install -r requirements.txt

If you need to run this locally, please contact Sam or Carlos for
the private key to access the spreadsheet from the script.

"""

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

##############################################################################
# Data Loading

def load_credentials():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        '.credentials/service-account-key.json',
        scope)
    return credentials

def context(credentials):
    return gspread.authorize(credentials)

def load_sheet_by_name(gc, name):
    result = [v for v in gc.worksheets() if v.title == name]
    if len(result) == 0: raise Exception("Could not find '%s' sheet" % name)
    if len(result) > 1: raise Exception("Too many '%s' sheets" % name)
    return result[0]

def get_spreadsheet(name):
    return context(load_credentials()).open(name)

##############################################################################
# Poor man's RDBMS

def inner_join(lst1, lst2, column):
    result = []
    index_lst2 = dict((v[column], v) for v in lst2)
    for el in lst1:
        if el[column] in index_lst2:
            row = el.copy()
            row.update(index_lst2[el[column]])
            result.append(row)
    return result

def group_by(lst, selector=None, key=None):
    result = {}
    if selector is None and not key is None:
        selector=lambda row: row[key]
    for item in lst:
        k = selector(item)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return [{'Key': k, 'Value': value} for (k, value) in result.iteritems()]

def group_by_pairs(lst, selector):
    result = []
    for d in group_by(lst, selector):
        result.append((d['Key'], d['Value']))
    return result

def recolumn(lst, old_column, new_column):
    result = []
    for item in lst:
        item = item.copy()
        v = item[old_column]
        del item[old_column]
        item[new_column] = v
        result.append(item)
    return result

def column(name):
    def f(item): return item[name]
    return f
