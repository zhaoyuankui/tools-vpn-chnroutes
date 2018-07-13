#!/bin/bash

declare routes_file='';
declare default_routes_file='./routes.txt';
declare request_ips_file='./request_ips';
declare ovpn_server_conf='/etc/openvpn/server.conf';

function show_help() {
    echo "Usage:";
    echo "    sh chnroute.sh [ROUTE_FILE]";
    echo "    If the ROUTE_FILE is not assigned, the file 'routes.txt'";
    echo "in the current directory will be used.";
    echo "Prerequisites:";
    echo "    The 'request_ips' must be exist in the current directory.";
    if [ "$1" == 1 ]; then
        exit 1;
    fi
}

function check_params() {
    if [ ! -f "$request_ips_file" ]; then
        sh prepare_request_ips.sh || show_help 1;
    fi
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

function prepare_routes_file() {
    python ./chnroutes.py || show_help 1;
    return 0;
}

function remove_old() {
    if [ -f "$ovpn_server_conf" ]; then
        sed -i '/\s*route.*net_gateway/,$d' "$ovpn_server_conf";
    fi
    return 0;
}

function add_routes() {
    declare push_routes_file="push_routes.txt";
    python prepare_push_routes.py "$request_ips_file" "$routes_file" "$push_routes_file";
    if [ -f "$ovpn_server_conf" ]; then
        cat "$push_routes_file" >> "$push_routes_file";
        rm -f "$push_routes_file";
    fi
    return 0;
}

function run() {
    check_params "${@}";
    remove_old;
    add_routes;
}

run "${@}";
