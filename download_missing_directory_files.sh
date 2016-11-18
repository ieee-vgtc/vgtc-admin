#!/bin/bash

for d in `find . -type d | tail -n +2 | sed 's/^.\///'`; do
    url=http://vgtc.org/$d
    result=`curl -sI $url | head -n 1`
    echo "$result"
    echo "HTTP/1.1 200 OK"
    if [ "$result" == "HTTP/1.1 200 OK" ]; then
	echo Found $url
    else
	echo Not found $url
    fi
done
