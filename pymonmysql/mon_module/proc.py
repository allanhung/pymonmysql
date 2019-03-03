#!/usr/bin/python

"""
show mysql process

Usage:
  pymonmysql proc list [--user USER] [--password PASSWORD] [--host HOST] [--port PORT] [--querytime QTIME] [--rc RC]
  pymonmysql proc export [--user USER] [--password PASSWORD] [--host HOST] [--port PORT] [--querytime QTIME]
  pymonmysql proc kill [--user USER] [--password PASSWORD] [--host HOST] [--port PORT] [--querytime QTIME]

Options:
  --user USER               database login user [default: root]
  --password PASSWORD       database login password
  --host HOST               database host [default: localhost]
  --port PORT               database port [default: 3306]
  --querytime QTIME         sql running time
  --rc RC                   return recoed count
  -h --help                 Show this screen.
"""

import common
import time
from pprint import pprint

def list(args):
    myobj = common.MyMon(host=args['--host'],user=args['--user'],password=args['--password'])
    query = "select * from information_schema.PROCESSLIST where command <> 'Sleep' and user not in ('event_scheduler', 'root', 'system user')"
    if args['--querytime']:
        query += " and time > {}".format(args['--querytime'])
    query = "{} order by time desc limit {}".format(query, args['--rc']) if args['--rc'] else "{} order by time desc".format(query)
    qr = myobj.execute(query)
    pprint(qr)
    return qr

def export(args):
    myobj = common.MyMon(host=args['--host'],user=args['--user'],password=args['--password'])
    query = "select * from information_schema.PROCESSLIST where command <> 'Sleep' and user not in ('event_scheduler', 'root', 'system user')"
    if args['--querytime']:
        query += " and time > {}".format(args['--querytime'])
    output_filename = '/tmp/mysql_proc_{}.txt'.format(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    qr = myobj.execute("{} order by time desc".format(query))
    with open(output_filename, 'w') as f:
        for row in qr:
            f.write("{}\n".format(row))
    return output_filename

def kill(args):
    myobj = common.MyMon(host=args['--host'],user=args['--user'],password=args['--password'])
    query = "select concat('kill ', id, ';') as kill_command from information_schema.PROCESSLIST where command <> 'Sleep' and user not in ('event_scheduler', 'root', 'system user')"
    if args['--querytime']:
        query += " and time > {}".format(args['--querytime'])
    qr = myobj.execute(query+" order by time desc")
    for row in qr:
        myobj.execute(row['kill_command']) 
    return query
