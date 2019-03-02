#!/usr/bin/python

"""
check mysql replication

Usage:
  pymonmysql repl check [--user USER] [--password PASSWORD] [--host HOST] [--port PORT]
  pymonmysql repl start_slave [--user USER] [--password PASSWORD] [--host HOST] [--port PORT] [--channel CHANNEL]

Options:
  --user USER               database login user [default: root]
  --password PASSWORD       database login password
  --host HOST               database host [default: localhost]
  --port PORT               database port [default: 3306]
  --channel CHANNEL         replication channel
  -h --help                 Show this screen.
"""

import common

def check(args):
    myobj = common.MyMon(host=args['--host'],user=args['--user'],password=args['--password'])
    qr = myobj.execute('SHOW SLAVE STATUS')
    c = {}
    for row in qr:
        value = {'io_running': row['Slave_IO_Running'], \
                 'sql_running': row['Slave_SQL_Running'], \
                 'error_no': row['Last_Errno'], \
                 'error': row['Last_Error'], \
                 'seconds_behind_master': row['Seconds_Behind_Master']}
        if 'Channel_Name' not in row.keys() or not row['Channel_Name']:
            c['None']=value
        else:
            c[row['Channel_Name']]=value
    return c

def start_slave(args):
    myobj = common.MyMon(host=args['--host'],user=args['--user'],password=args['--password'])
    if args['--channel']:
        qr = myobj.execute("START SLAVE FOR CHANNEL '{}'".format(args['--channel']))
    else:
        qr = myobj.execute("START SLAVE")
