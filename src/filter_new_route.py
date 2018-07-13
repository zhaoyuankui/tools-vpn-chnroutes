#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: filter_new_route.py
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

def save_route(ovpn_conf, route, ip):
    ovpn_conf_file = open(ovpn_conf, 'a');
    ovpn_conf_file.write('push "route %s %s net_gateway 5"\n' % (route[0], route[1]));
    ovpn_conf_file.close();
    print 'route %s %s %s' % (route[0], route[1], ip);

def init_routes_map(routes_map, ovpn_conf):
    ovpn_conf_file = open(ovpn_conf, 'r');
    for line in ovpn_conf_file:
        if (-1 == line.find('net_gateway')):
            continue;
        route_segments = line.split(' ');
        if (len(route_segments) < 4):
            print "Error push route line: %s." % line.strip();
            continue;
        routes_map[route_segments[2]] = 1;
    ovpn_conf_file.close();

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
    routes_file = args[1];
    ovpn_conf = args[2];

    chnroutes = prepare_routes(routes_file);
    ip = '';
    routes_map = {};
    init_routes_map(routes_map, ovpn_conf);
    while True:
        ip = sys.stdin.readline();
        if '' == ip:
            break;
        route = process_ip(ip, chnroutes);
        if (None == route):
            print "%s doesn't found route." % ip;
            continue;
        if (route[0] in routes_map):
            continue;
        routes_map[route[0]] = 1;
        save_route(ovpn_conf, route, ip);

if __name__ == "__main__":
    logfile = open('/var/tmp/filter_new_route.log', 'w');
    sys.stdout = logfile;
    run(sys.argv);
    logfile.close();
