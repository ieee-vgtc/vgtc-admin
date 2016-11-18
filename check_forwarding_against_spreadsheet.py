#!/usr/bin/env python

"""

Checks consistency of mailing lists.

This script does three things at present:

1) check whether the mailing lists on google apps matches the
   data from the google spreadsheet

2) check whether subcommittees with specific mailing lists have the
   right members. Currently this only means that the papers chairs are
   split in three subgroups (VAST, InfoVis and SciVis)

3) check whether the global mailing list (organizing_committee@ieeevis.org)
   contains exactly all members of the organizing committee (as defined by
   the 'Organizing Committee' column on the spreadsheet

The script generates a report output in JSON format (which is displayed
in a user-readable format by our monitoring webpages)

"""

from data import *
from googlestuff import *


admin = get_admin()
cID = "C01ilvq9c" # This is the customer ID for vgtc's G-suite org
##############################################################################

def generate_list_of_mailing_lists():
    """ get mailing lists from google apps """
    groups = admin.groups()
    members = admin.members()
    result = []
    for group in call_google(groups.list(customer=cID))["groups"]:
        v = list(member['email']
                 for member in
                 call_google(members.list(groupKey=group['email'])).get("members", []))
        result.append({"Address": group['email'],
                       "Forwards": v})
    return result

def generate_roster_from_spreadsheet():
    gc = context(load_credentials()).open('VIS2016_roster_clean')
    people = load_sheet_by_name(gc, 'VIS 2017 People').get_all_records()
    roles = load_sheet_by_name(gc, 'Roles').get_all_records()
    return inner_join(recolumn(group_by(people, key='Role'), 'Key', 'Role'),
                      roles, 'Role')

def fix_mailing_list(address, roster, current=None):
    if address == '':
        return
    if current is None:
        current = list_group(address)
    members = admin.members()
    to_add = list(roster - current - set(['']))
    to_remove = list(current - roster - set(['']))
    remove_from_group(address, to_remove)
    add_to_group(address, to_add)

def generate_oc_mailing_list(roster):
    emails = set()
    for role in roster:
        if role['Organizing Committee'] <> 'TRUE':
            continue
        for l in role['Value']:
            if l['Email'] <> '':
                emails.add(l['Email'].lower())
    return emails

def generate_mismatches():
    all = False
    doml = dict((ml['Address'], ml['Forwards'])
                for ml in generate_list_of_mailing_lists())
    roster = generate_roster_from_spreadsheet()
    for role in roster:
        address = role['Address']
        roster_emails = set(v['Email'] for v in role['Value']) - set([''])
        mailing_list = set(doml.get(address, [])) - set([''])
        print "Mailing list %s" % address
        if address == '':
            continue
        if roster_emails <> mailing_list:
            print "  set mismatch:"
            print "    Roster says:", roster_emails
            print "    Google says:", mailing_list
            print "  Act?"
            if not all:
                x = raw_input()
            if all or x[0].lower() in ['y', 'a']:
                if x[0].lower() == 'a':
                    all = True
                fix_mailing_list(address, roster_emails, mailing_list)
        else:
            print "  OK!"
    oc_mailing_list = generate_oc_mailing_list(roster)
    fix_mailing_list('organizing_committee@ieeevis.org',
                     oc_mailing_list)

if __name__ == '__main__':
    # print generate_list_of_mailing_lists()
    # print generate_roster_from_spreadsheet()
    print generate_mismatches()
    # print generate_oc_mailing_list(generate_roster_from_spreadsheet())
  
