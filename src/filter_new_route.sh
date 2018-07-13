#!/bin/bash

declare routes_file='';
declare default_routes_file='./routes.txt';
declare ovpn_conf='./server.conf';


function show_help() {
    echo "Usage:";
    echo "    sh filter_new_route.sh [ROUTE_FILE]";
    echo "    If the ROUTE_FILE is not assigned, the file 'routes.txt'";
    echo "in the current directory will be used.";
    if [ "$1" == 1 ]; then
        exit 1;
    fi
}

function prepare_routes_file() {
    python ./chnroutes.py || show_help 1;
    return 0;
}

function check_params() {
    if [ $# -gt 1 ]; then
        show_help 1;
    fi
    if [ $# -eq 1 -a -f "$1" ]; then
        routes_file="$1";
        return;
    fi
    if [ $# -eq 1 ]; then
        echo "The file assigned is not normal file or not exist.";
        show_help 1;
    fi
    if [ -f "$default_routes_file" ]; then
        routes_file="$default_routes_file";
    fi
    if [ ! "$routes_file" ]; then
        echo "Prepare routes file from server.";
        prepare_routes_file;
    fi
    if [ ! "$routes_file" ]; then
        echo "Routes file not exist.";
        show_help 1;
    fi
}

function run() {
    check_params "${@}";
    tcpdump -xXnnvvSs 64 -i eth0 | grep '^\s*45.76.50.135.*>' | grep -o '>\s*[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*' | awk '{print $NF}' | python filter_new_route.py "$routes_file" "$ovpn_conf";
}

run "${@}";
