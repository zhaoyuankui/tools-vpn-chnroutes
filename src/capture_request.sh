#!/bin/bash

sudo tcpdump -xXnnvvSs 64 -i en0 | grep '\s*192.168.* > ' | grep -v '8888' | awk '{print $3}' >> /var/tmp/request_ips &
