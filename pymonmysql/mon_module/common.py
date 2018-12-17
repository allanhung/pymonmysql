import subprocess
import pymysql

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

    def execute(self, query, args=None):
        cursor = self._connect().cursor()
        cursor.execute(query, args)
        return cursor.fetchall()

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
