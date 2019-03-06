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
import proc
from docopt import docopt

def run(args):
    mailsubject = ''
    mailmsg = []
    myconfig = common.readconfig(args['--config'])
    mymail = common.EmailHelper(myconfig['email']['smtp_host'], myconfig['email']['receiver'])
    myslack = common.SlackHelper(myconfig['slack']['url'])

    # replication status
    repl_args = docopt(repl.__doc__, argv=['repl', 'check'])
    repl_args.update(myconfig['repl']) 
    repl_args.update(myconfig['proc']) 
    try:
        repl_status = repl.check(repl_args)
        for channel, column in repl_status.items():
            if 'test_tcp_connect' in myconfig['repl'].keys() and myconfig['repl']['test_tcp_connect']:
                connected, tcpmsg = myos.check_port(column['master_host'], column['master_port'])
                if not connected:
                    if not mailsubject:
                        mailsubject = 'Connection to {} on port {} failed'.format(column['master_host'], column['master_port'])
                    mailmsg.append(debugmsg(tcpmsg))
            if column['io_running'] <> 'Yes' or column['sql_running'] <> 'Yes':
                if column['io_running'] <> 'Yes' and 'auto_slave_restart' in myconfig['repl'].keys() and myconfig['repl']['auto_slave_restart']:
                    repl_args.update({'--channel': channel})
                    repl.start_slave(repl_args)
                    r = 'channel {} is not running, try to auto restart.'.format(channel)
                else:
                    r = 'channel {} is not running.'.format(channel)
                if not mailsubject:
                    mailsubject = r
                mailmsg.append(replmsg(r, channel, column))
            elif column['seconds_behind_master'] > myconfig['repl']['seconds_behind_master']:
                r = 'channel {} replication latency is more than {} secs.'.format(channel, myconfig['repl']['seconds_behind_master'])
                if not mailsubject:
                    mailsubject = r
                mailmsg.append(replmsg(r, channel, column))
    except Exception as e:
        if not mailsubject:
            mailsubject = 'monitor program error when check replication'
            mailmsg.append(expectmsg(r, e))

    # os size
    os_size = myos.size(args)
    for mount_point, column in os_size.items():
        if column['percent'] > myconfig['myos']['percentage']:
            r = 'The size of mount point {} size is over {}%.'.format(mount_point, myconfig['myos']['percentage'])
            if not mailsubject:
                mailsubject = r
            mailmsg.append(diskmsg(r, mount_point, column))

    # os loadavg
    if 'load' in myconfig['myos'].keys():
        os_load = myos.load(args)
        for avg_period, avg_load in os_load.items():
            if avg_load > myconfig['myos']['load']:
                r = 'The load average {} is {} over {}.'.format(avg_period, avg_load, myconfig['myos']['load'])
                if not mailsubject:
                    mailsubject = r
                mailmsg.append(loadmsg(r, avg_period, avg_load))
                break

    # oom check
    if 'oom' in myconfig['myos'].keys():
        oom = myos.oom(myconfig['myos']['oom'])
        if oom:
            r = 'kernel: Out of Memory'
            if not mailsubject:
                mailsubject = r
            mailmsg.append(oommsg(r, oom))

    # proc
    try:
        if 'proc' in myconfig.keys():
            top_procs = proc.list(repl_args)
            if top_procs:
                r = 'There are queries running more than {} secs.'.format(myconfig['proc']['--querytime'])
                if not mailsubject:
                    mailsubject = r
                mailmsg.append(procmsg(r, top_procs))
    except Exception as e:
        if not mailsubject:
            mailsubject = 'monitor program error when check processlist'
            mailmsg.append(expectmsg(r, e))

            
    if mailsubject:        
        myslack.send(myconfig['slack']['channel'], '\n\n'.join(mailmsg))
        mymail.send_email(mailsubject, '\n\n'.join(mailmsg))
    else:
        print(repl_status)
        print(os_size)
        print(os_load)

def oommsg(reason, msg):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    mailmsg.extend(msg)
    return '\n'.join(mailmsg)

def expectmsg(reason, msg):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    mailmsg.append('error message: {}'.format(msg))
    return '\n'.join(mailmsg)

def debugmsg(msg):
    mailmsg = []
    mailmsg.append('========== debug ==========')
    mailmsg.extend(msg)
    return '\n'.join(mailmsg)

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
    
def loadmsg(reason, period, load):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    mailmsg.append('            {} load: {}'.format(period, load))
    return '\n'.join(mailmsg)
    
def procmsg(reason, procs):
    mailmsg = []
    mailmsg.append('========== '+reason+' ==========')
    for proc in procs:
        mailmsg.append('time: {} secs'.format(proc['TIME']))
        mailmsg.append('user: {}'.format(proc['User']))
        mailmsg.append('host: {}'.format(proc['Host']))
        mailmsg.append('query: {}'.format(proc['INFO']))
    return '\n'.join(mailmsg)
