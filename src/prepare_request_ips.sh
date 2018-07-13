#!/bin/bash

cat  /var/tmp/request_ips | grep -o '^[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | sort | uniq > request_ips
# write back to slim it.
if [ 0 -eq $? ]; then
cat ./request_ips > /var/tmp/request_ips;
fi
