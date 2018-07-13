#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: prepare_push_routes.py
Author: kevin(kevin@baidu.com)
Date: 2018/03/27 18:32:36
"""

import sys;
import socket;
import struct;

class RouteBTree:
    left = None;
    right = None;
    leaf = None;

    def __init__(self, left = None, right = None, leaf = None):
        self.left = left;
        self.right = right;
        self.leaf = leaf;

def get_mask_len(mask_n):
    count = 0;
    while mask_n > 0:
        mask_n = mask_n & (mask_n - 1);
        count = count + 1;
    return count;

def add_btree_node(btree, net, mask):
    net_n = socket.ntohl(struct.unpack("I",socket.inet_aton(str(net)))[0]);
    mask_n = socket.ntohl(struct.unpack("I",socket.inet_aton(str(mask)))[0]);
    mask_len = get_mask_len(mask_n);
    bit_mask = 0x80000000;
    p_node = btree;
    for i in range (0, mask_len):
        bit_flag = bit_mask & net_n;
        # Add the node if it's None.
        if (0 == bit_flag and None == p_node.left):
            p_node.left = RouteBTree();
        if (0 != bit_flag and None == p_node.right):
            p_node.right = RouteBTree();
        # Traverse down the tree.
        if (0 == bit_flag):
            p_node = p_node.left;
        else:
            p_node = p_node.right;
        # Add the route info to the leaf.
        if (i + 1 == mask_len):
            p_node.leaf = (net, mask);
        bit_mask = bit_mask >> 1;


def prepare_routes(routes_file):
    btree = RouteBTree();
    for route in file(routes_file, 'r'):
        route_segments = route.split(" ");
        if len(route_segments) < 3:
            print "Error line: %s" % route;
            continue;
        net = route_segments[1];
        mask = route_segments[2];
        add_btree_node(btree, net, mask);
    return btree;

def save_routes(result_file, push_routes):
    for net in push_routes.keys():
        route = push_routes[net][0];
        iplist = push_routes[net][1];
        result_file.write('push "route %s %s net_gateway 5"\n' % (net, route[1]));
        print 'route %s %s %s' % (net, route[1], '|'.join(iplist));

def process_ip(ip, chnroutes):
    try:
        ip_n = socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0]);
    except:
        print "Incorrect ip %s" % ip;
        return None;
    bit_mask = 0x80000000;
    p_node = chnroutes;
    p_last_leaf = None;
    while (None != p_node):
        bit_flag = bit_mask & ip_n;
        if (0 == bit_flag):
            p_node = p_node.left;
        else:
            p_node = p_node.right;
        if (None == p_node):
            break;
        if (None != p_node.leaf):
            p_last_leaf = p_node.leaf;
        bit_mask = bit_mask >> 1;
    return p_last_leaf;

def run(args):
    request_ips_file = args[1];
    routes_file = args[2];
    push_routes_file = args[3];

    chnroutes = prepare_routes(routes_file);
    result_file = file(push_routes_file, 'w');
    push_routes = {};
    for ip in file(request_ips_file, 'r'):
        route = process_ip(ip, chnroutes);
        if (None == route):
            print "%s doesn't found route." % ip;
            continue;
        if (not push_routes.has_key(route[0])):
            push_routes[route[0]] = (route, [ip.strip()]);
        else:
            push_routes[route[0]][1].append(ip.strip());
    save_routes(result_file, push_routes);
    result_file.close();

if __name__ == "__main__":
    logfile = open('./log', 'w');
    sys.stdout = logfile;
    run(sys.argv);
    logfile.close();
