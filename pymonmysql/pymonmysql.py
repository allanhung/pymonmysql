#!/usr/bin/python

"""pymonmysql

mysql monitor toolkit

Usage:
  pymonmysql <module> <func> [<args>...]

Options:
  -h --help            Show this screen.
"""

from docopt import docopt
import sys
import mon_module
from mon_module import *

def main():
    """
    run module

    example:
    pymonmysql task track --trackid xxx
    """
    config_file = '/etc/pymonmysql.yml'
    args = docopt(__doc__, options_first=True)
    module = args['<module>']
    func = args['<func>']
    argv = [module, func]+args['<args>']
    module_script = getattr(mon_module, module)
    module_args = docopt(module_script.__doc__, argv=argv)
    return getattr(module_script, func)(module_args)

if __name__ == '__main__':
    main()
