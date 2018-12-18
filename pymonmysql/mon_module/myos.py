#!/usr/bin/python

"""
check os mount point size

Usage:
  pymonmysql myos size

Options:
  -h --help                 Show this screen.
"""

import common

def size(args):
    d = {}
    for l in file('/proc/mounts'):
        if l[0] == '/':
            l = l.split()
            if l[1] <> '/boot':
                t, u, f, p = common.disk_usage(l[1])
                d[l[1]]= {'total':t, 'used':u, 'free':f, 'percent': p}
    return d
