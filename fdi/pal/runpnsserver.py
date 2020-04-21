#!flask/bin/python
# -*- coding: utf-8 -*-

# This is to be able to test w/ or w/o installing the package
# https://docs.python-guide.org/writing/structure/
#from pycontext import spdc
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..')))

# print(sys.path)
import spdc


from spdc.pns import logdict  # import logdict
import logging
import logging.config
# create logger
logging.config.dictConfig(logdict.logdict)
logger = logging.getLogger()
logger.debug('logging level %d' % (logger.getEffectiveLevel()))

from spdc.pal.pnspoolserver import app
from spdc.pns.options import opt

from spdc.pns.pnsconfig import pnsconfig as pc

# default configuration is provided. Copy pnsconfig.py to ~/local.py
import sys
from os.path import expanduser, expandvars
env = expanduser(expandvars('$HOME'))
sys.path.insert(0, env)
try:
    from local import pnsconfig as pc
except Exception:
    pass

if __name__ == '__main__':

    logger.info(
        'PNS poold  Server starting. Make sure no other instance is running')
    node, verbose = opt(pc['node'])
    pc['node'].update(node)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info('logging level %d' % (logger.getEffectiveLevel()))
    if node['username'] in ['', None] or node['password'] in ['', None]:
        logger.error(
            'Error. Specify non-empty username and password on commandline')
        exit(3)

    app.run(host=node['host'], port=node['port'],
            threaded=False, debug=verbose, processes=5)
