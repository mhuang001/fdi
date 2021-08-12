#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" https://livecodestream.dev/post/python-flask-api-starter-kit-and-project-layout/ """

from fdi._version import __version__
from flask import Flask
from flasgger import Swagger
from httppool.route.home import home_api

from fdi.utils import getconfig

import logging
import sys

#sys.path.insert(0, abspath(join(join(dirname(__file__), '..'), '..')))

# print(sys.path)


def setuplogging(level=logging.WARN):
    global logging
    # create logger
    logging.basicConfig(stream=sys.stdout,
                        format='%(asctime)s-%(levelname)4s'
                        '-[%(filename)6s:%(lineno)3s'
                        '-%(funcName)10s()] - %(message)s',
                        datefmt="%Y%m%d %H:%M:%S")
    logging.getLogger("requests").setLevel(level)
    logging.getLogger("filelock").setLevel(level)
    if sys.version_info[0] > 2:
        logging.getLogger("urllib3").setLevel(level)
    return logging


def create_app(conf=None):
    app = Flask(__name__)

    app.config['SWAGGER'] = {
        'title': 'FDI %s HTTPpool Server' % __version__,
    }
    swagger = Swagger(app)

    app.register_blueprint(home_api, url_prefix=pc['baseurl'])

    return app


if __name__ == '__main__':

    logger = logging.getLogger()
    # default configuration is provided. Copy config.py to ~/.config/pnslocal.py
    pc = getconfig.getConfig()

    lv = pc['logginglevel']
    logger.setLevel(lv)
    setuplogging(lv if lv > logging.WARN else logging.WARN)
    logger.info(
        'Server starting. Make sure no other instance is running.'+str(lv))

    node = pc['node']
    # Get username and password and host ip and port.

    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true', help='Be verbose.')
    parser.add_argument('-u', '--username',
                        default=node['username'], type=str, help='user name/ID')
    parser.add_argument('-p', '--password',
                        default=node['password'], type=str, help='password')
    parser.add_argument('-i', '--host',
                        default=node['host'], type=str, help='host IP/name')
    parser.add_argument('-o', '--port',
                        default=node['port'], type=int, help='port number')
    parser.add_argument('-s', '--server', default='httppool_server',
                        type=str, help='server type: pns or httppool_server')
    parser.add_argument('-w', '--wsgi', default=False,
                        action='store_true', help='run a WSGI server.')
    args = parser.parse_args()

    verbose = args.verbose
    node['username'] = args.username
    node['password'] = args.password
    node['host'] = args.host
    node['port'] = args.port
    servertype = args.server
    wsgi = args.wsgi

    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info('logging level %d' % (logger.getEffectiveLevel()))
    if node['username'] in ['', None] or node['password'] in ['', None]:
        logger.error(
            'Error. Specify non-empty username and password on commandline')
        exit(3)
    print('Check http://' + node['host'] + ':' + str(node['port']) +
          '/apidocs' + ' for API documents.')

    if servertype == 'pns':
        print('======== %s ========' % servertype)
        #from fdi.pns.pns_server import app
        sys.exit(1)
    elif servertype == 'httppool_server':
        print('<<<<<< %s >>>>>' % servertype)
        #from fdi.pns.httppool_server import app
        app = create_app(pc)
    else:
        logger.error('Unknown server %s' % servertype)
        sys.exit(-1)

    if wsgi:
        from waitress import serve
        serve(app, url_scheme='https', host=node['host'], port=node['port'])
    else:
        app.run(host=node['host'], port=node['port'],
                threaded=True, debug=verbose, processes=1, use_reloader=True)
