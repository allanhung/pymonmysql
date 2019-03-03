#!/usr/bin/python

"""
check os mount point size

Usage:
  pymonmysql myos size
  pymonmysql myos load

Options:
  -h --help                 Show this screen.
"""

import common
import os
import time
import socket

def size(args):
    d = {}
    for l in file('/proc/mounts'):
        if l[0] == '/':
            l = l.split()
            if l[1] <> '/boot':
                t, u, f, p = common.disk_usage(l[1])
                d[l[1]]= {'total':t, 'used':u, 'free':f, 'percent': p}
    return d

def load(args):
    (a, b, c) = os.getloadavg()
    return {'1min': a, '5min': b, '15min': c} 

def check_port(address, port):
    # Create a TCP socket   
    msg = []
    s = socket.socket()
    msg.append("%s, Attempting to connect to %s on port %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port))
    try:
        s.connect((address, port))
        s.settimeout(2)
        msg.append("%s, Connected to %s on port %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port))
    except socket.error, e:
        msg.append("%s, Connection to %s on port %s failed: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port, e))
    return msg
