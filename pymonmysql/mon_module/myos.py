#!/usr/bin/python

"""
check os mount point size

Usage:
  pymonmysql myos size
  pymonmysql myos load
  pymonmysql myos oom [--period PERIOD]

Options:
  -h --help                 Show this screen.
  --period PERIOD           check period (mins)
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

def oom(args):
    oom = []
    retcode, result = common.check_output(["grep -i 'killed process' /var/log/messages"], shell=True)
    if not retcode:
        current_year = time.strftime("%Y")
        if args['--period']:
            time_start = time.time()-60*int(args['--period'])
            for row in reversed(result.strip().split("\n")):
                if time.mktime(time.strptime(current_year+' '+row[:15], '%Y %b %d %H:%M:%S')) > time_start:
                    oom.append(row)
                else:
                    break
        else:
            for row in reversed(result.strip().split("\n")):
                oom.append(row)
    return oom    

def check_port(address, port):
    # Create a TCP socket   
    msg = []
    connected = True
    s = socket.socket()
    msg.append("%s, Attempting to connect to %s on port %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port))
    try:
        s.connect((address, port))
        s.settimeout(2)
        msg.append("%s, Connected to %s on port %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port))
        connected = True
    except socket.error, e:
        msg.append("%s, Connection to %s on port %s failed: %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), address, port, e))
        connected = False
    return connected, msg
