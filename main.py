#!/usr/bin/env python

# FIXME: This script is horribly named.

##############################################################################

from __future__ import print_function
from data import *
import sys
from googlestuff import *

def check_groups_against_spreadsheet(act_on_check=False):
    members = get_admin().members()
    groups = get_admin().groups()

    doc = get_spreadsheet("VIS2016_roster_clean")
    roles_sheet = load_sheet_by_name(doc, "Roles").get_all_records()
    people_sheet = load_sheet_by_name(doc, "VIS 2017 People").get_all_records()
    roles = [role for role in roles_sheet if role["Address"] <> '']

    people_by_role = inner_join(recolumn(group_by(people_sheet, lambda key: key["Role"]),
                                         "Key",
                                         "Role"),
                                roles, "Role")

    for row in people_by_role:
        if row["Address"] == "web@ieeevis.org":
            continue
        member_list = call_google(members.list(groupKey=row["Address"]))
        current_list_members = set(v['email'] for v in member_list.get('members', []))
        roster_members = set(v['Email'] for v in row['Value'])
        a_minus_b = current_list_members.difference(roster_members)
        b_minus_a = roster_members.difference(current_list_members)
        if len(a_minus_b) > 0:
            print("Need to unsubscribe from %s:" % row["Address"])
            for e in a_minus_b:
                print("  " + e)
                if act_on_check:
                    k = members.delete(groupKey=row["Address"],
                                       memberKey=e)
                    call_google(k)
                
        if len(b_minus_a) > 0:
            print(current_list_members)
            print(roster_members)
            print("Need to subscribe to %s:" % row["Address"])
            for e in b_minus_a:
                print("  " + e)
                if act_on_check:
                    k = members.insert(groupKey=row["Address"],
                                       body={"email": e,
                                             "role": 'MEMBER'})
                    try:
                        call_google(k)
                    except Exception, e:
                        print(e)
        if len(a_minus_b) == 0 and len(b_minus_a) == 0:
            print("List %s is OK." % row["Address"])

    # for role in roles:
    #     group = call_google(groups.get(groupKey=role["Address"]))
    #     member_list = call_google(members.list(groupKey=role["Address"]))
        

if __name__ == '__main__':
    act = False
    try:
        act = sys.argv[1] == 'ACT'
    except:
        pass
    print(check_groups_against_spreadsheet(act))
    # create_all_groups()
