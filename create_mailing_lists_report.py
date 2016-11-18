#!/usr/bin/env python

##############################################################################

from __future__ import print_function
from data import *
import sys
from googlestuff import *

admin = get_admin()

cID = "C01ilvq9c" # This is the customer ID for vgtc's G-suite org

def main():
    groups = admin.groups()
    members = admin.members()
    for group in call_google(groups.list(customer=cID))["groups"]:
        print("Mailing list %s" % group['email'])
        for member in call_google(members.list(groupKey=group['email'])).get("members", []):
            print ("  %s" % member['email'])
        print("\n")

if __name__ == '__main__':
    main()
