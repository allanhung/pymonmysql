#!/usr/bin/python

"""
mysql dump schema

Usage:
  pymonmysql repl check [--user USER] [--password PASSWORD] [--host HOST] [--port PORT]

Options:
  --user USER               database login user [default: root]
  --password PASSWORD       database login password
  --host HOST               database host [default: localhost]
  --port PORT               database port [default: 3306]
  -h --help                 Show this screen.
"""

import common

def check(args):
    args_dict={k[2:]:v for k, v in args.items()}
    myobj = common.MyMon(host=args_dict['host'],user=args_dict['user'],password=args_dict['password'])
    qr = myobj.execute('SHOW SLAVE STATUS')
    print(qr)
