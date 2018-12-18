#!/usr/bin/python

"""
monitor mysql from crontab

Usage:
  pymonmysql cron run [--config CONFIG]

Options:
  --config CONFIG           config file [default: /etc/pymonmysql.yml]
  -h --help                 Show this screen.
"""

import common
import repl
import myos
from docopt import docopt

def run(args):
    mailsubject = ''
    mailmsg = []
    myconfig = common.readconfig(args['--config'])
    mymail = common.EmailHelper(myconfig['email']['smtp_host'], myconfig['email']['receiver'])
    repl_args = docopt(repl.__doc__, argv=['repl', 'check'])
    repl_args.update(myconfig['repl']) 
    repl_status = repl.check(repl_args)
    for channel, column in repl_status.items():
        if column['io_running'] <> 'Yes' or column['sql_running'] <> 'Yes':
            r = 'channel {} is not running.'.format(channel)
            if not mailsubject:
                mailsubject = r
            mailmsg.append(r)
            mailmsg.append(replmsg(r, channel, column))
        elif column['seconds_behind_master'] > myconfig['repl']['seconds_behind_master']:
            r = 'channel {} replication latency is more than {} secs.'.format(channel, myconfig['repl']['seconds_behind_master'])
            if not mailsubject:
                mailsubject = r
            mailmsg.append(replmsg(r, channel, column))
    os_size = myos.size(args)
    for mount_point, column in os_size.items():
        if column['percent'] > myconfig['myos']['percentage']:
            r = 'The size of mount point {} size is over {}%.'.format(mount_point, myconfig['myos']['percentage'])
            if not mailsubject:
                mailsubject = r
            mailmsg.append(diskmsg(r, mount_point, column))
    if mailsubject:        
        mymail.send_email(mailsubject, '\n\n'.join(mailmsg))
    else:
        print(repl_status)
        print(os_size)

def replmsg(reason, channel, column):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    mailmsg.append('         channel_name: {}'.format(channel))
    mailmsg.append('           io_running: {}'.format(column['io_running']))
    mailmsg.append('          sql_running: {}'.format(column['sql_running']))
    mailmsg.append('             error_no: {}'.format(column['error_no']))
    mailmsg.append('                error: {}'.format(column['error']))
    mailmsg.append('seconds_behind_master: {}'.format(column['seconds_behind_master']))
    return '\n'.join(mailmsg)

def diskmsg(reason, mount_point, column):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    mailmsg.append('          mount_point: {}'.format(mount_point))
    mailmsg.append('                total: {}'.format(column['total']))
    mailmsg.append('                 used: {}'.format(column['used']))
    mailmsg.append('                 free: {}'.format(column['free']))
    mailmsg.append('           percentage: {}'.format(column['percent']))
    return '\n'.join(mailmsg)
