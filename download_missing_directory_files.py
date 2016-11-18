#!/usr/bin/env python

import sys
import subprocess

for d in subprocess.check_output("find . -type d | tail -n +2 | sed 's/^.\///'", shell=True).split('\n'):
    url = 'http://vgtc.org/' + d
    result = subprocess.check_output("curl -sI %s | head -n 1" % url, shell=True).strip()
    if result == 'HTTP/1.1 200 OK':
        sys.stderr.write("%s %s.html\n" % (d, d))
        print "%s %s.html" % (d, d)
        subprocess.call("curl %s > %s.html" % (url, d), shell=True)
