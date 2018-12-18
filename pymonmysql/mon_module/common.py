from __future__ import division
import subprocess
import os
import socket
import math
import pymysql
import requests
import json
from contextlib import contextmanager
from pymysql.cursors import DictCursor
import smtplib
from email.mime.text import MIMEText
import yaml

class EmailHelper(object):
    def __init__(self, smtp_host, receiver):
        self._smtp_host = smtp_host
        self._sender = "root@%s" % socket.getfqdn()
        self._receiver = receiver

    def send_email(self, subject, msg):
        try:
            smtp = smtplib.SMTP(self._smtp_host)

            email_msg = MIMEText(str(msg))
            email_msg['Subject'] = subject
            email_msg['From'] = self._sender
            email_msg['To'] = ';'.join(self._receiver)

            print("Sending email to %s via %s with the subject '%s'" % (self._receiver, self._smtp_host, subject))
            smtp.sendmail(self._sender, self._receiver, email_msg.as_string())
            smtp.quit()
        except Exception as e:
            print("Failed to send email From: %s, To: %s" % (self._sender, self._receiver))
            print(str(e))
            return False

        return True

class SlackHelper(object):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    @staticmethod
    def construct_message(channel, long_message):
        message = {'channel': channel, 'username': socket.getfqdn(), 'text': long_message}
        return message

    def send(self, channel, long_message):
        message = self.construct_message(channel, long_message)
        myrequest = requests.post(self.webhook_url, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        if myrequest.status_code != 200:
            raise Exception('%s %s' % (myrequest.status_code, myrequest.reason))

class MyMon(object):
    def __init__(self, host='localhost', port=3306, user='root', password=None, socket=None):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.socket = socket

    @contextmanager
    def _connect(self):
        """Connect to ProxySQL admin interface."""
        if self.socket is not None:
            conn = pymysql.connect(unix_socket=self.socket,
                                   user=self.user,
                                   passwd=self.password,
                                   cursorclass=DictCursor)
        else:
            conn = pymysql.connect(host=self.host,
                                   port=self.port,
                                   user=self.user,
                                   passwd=self.password,
                                   cursorclass=DictCursor)

        yield conn
        conn.close()

    def execute(self, query):
        with self._connect() as conn:
            return execute(conn, query)

def execute(conn, query):
    """Execute query in connection"""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def readconfig(config_file):
    if os.path.exists(config_file):
        with open(config_file, 'r') as ymlfile:
             return yaml.load(ymlfile)
    else:
        return {}

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    percent = round((used / total) * 100)
    return humansize(total), humansize(used), humansize(free), percent

def humansize(size):
    SUFFIXES = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    for suffix in SUFFIXES:
        size /= 1024
        if size < 1024:
            return '{0:.1f} {1}'.format(size, suffix)

def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.
    Backported from Python 2.7 as it's implemented as pure python on stdlib.
    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    process.wait()
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output
