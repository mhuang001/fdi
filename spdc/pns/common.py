# -*- coding: utf-8 -*-
import os
import errno
from pprint import pprint, pformat
import json
import traceback

# HTTPConnection.debuglevel = 1


import sys
if sys.version_info[0] > 2:
    #from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.parse import urlsplit
    from urllib.error import HTTPError
    import requests
    from http.client import HTTPConnection
else:
    #from urllib import urlencode
    from urllib2 import urlopen
    from urlparse import urlsplit
    from urllib2 import HTTPError
    from httplib import HTTPConnection

from spdc.pns.logdict import logdict
import logging
logger = logging.getLogger(__name__)
logger.debug('level %d' % (logger.getEffectiveLevel()))


if 0:
    print(logger.propagate)
    print(logger.disabled)
    print(logger.filters)
    print(logger.hasHandlers())
    print(logger.handlers)
    print(logger.level)

from spdc.dataset.deserialize import deserializeClassID
from spdc.dataset.serializable import serializeClassID

commonheaders = {
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-type": 'application/json'
}


def trbk(e):
    """ trace back 
    """
    return ' '.join([x for x in
                     traceback.extract_tb(e.__traceback__).format()])


def getJsonObj(url, headers=None, usedict=False):
    """ return object from url. url can be http or file.
    translate keys and values from string to
    number if applicable. Return None if fails.
    Not using requests.get() as it cannot open file:/// w/o installing
    https://pypi.python.org/pypi/requests-file
    """
    logger.debug('url: %s' % (url))
    i = 1
    while True:
        try:
            stri = urlopen(
                url, timeout=15).read().decode('utf-8')
            #logger.debug('stri ' + stri)
            break
        except Exception as e:
            logger.debug(e)
            if issubclass(e.__class__, HTTPError):
                print(e.code)
                print('urllib   ' + e.read())
                ret = e
                return None
            if i >= 1:
                logger.error("Give up " + url + " after %d tries." % i)
                return None
            else:
                i += 1
    # print(url,stri)
    # ret = json.loads(stri, parse_float=Decimal)
    # ret = json.loads(stri, cls=Decoder,
    #               object_pairs_hook=collections.OrderedDict)
    ret = deserializeClassID(stri, usedict=usedict)
    #logger.debug(pformat(ret, depth=6)[:] + '...')
    logger.debug(str(ret)[:160] + '...')
    return ret


def jsonREST(url, obj, headers, cmd):
    """ generic RESTful command handler for POST, PUT, and DELETE.
    """
    js = serializeClassID(obj)
    # %s obj %s headers %s' % (url, obj, headers))
    logger.debug(url + js[:160])

    i = 1
    while True:
        try:
            if 0 and sys.version_info[0] > 2:
                if cmd == 'POST':
                    r = requests.post(
                        url, data=js, headers=headers, timeout=15)
                elif cmd == 'PUT':
                    r = requests.post(
                        url, data=js, headers=headers, timeout=15)
                elif cmd == 'DELETE':
                    r = requests.post(
                        url, data=js, headers=headers, timeout=15)
                else:
                    raise ValueError('Bad REST command ' + cmd)
                stri = r.text
            else:
                o = urlsplit(url)
                u = o.netloc
                p = o.path + '?' + o.query + '#' + o.fragment
                h = HTTPConnection(u, timeout=15)
                h.request(cmd, p, js, headers)
                r = h.getresponse()
                stri = r.read()
            # print('ps textx %s\nstatus %d\nheader %s' % (stri, r.status_code, r.headers))
            break
        except Exception as e:
            logger.debug(e)
            if i >= 1:
                logger.error("Give up %s %s after %d tries." % (cmd, url, i))
                return None
            else:
                i += 1

    # ret = json.loads(stri, parse_float=Decimal)
    # ret = json.loads(stri, cls=Decoder)
    ret = deserializeClassID(stri)
    logger.debug(str(ret)[:160] + '...')
    return ret


def postJsonObj(url, obj, headers):
    """ posts object to url. Returns None if fails.
    """

    return jsonREST(url, obj, headers, 'POST')


def putJsonObj(url, obj, headers):
    """ puts object to url. Returns None if fails.
    """
    return jsonREST(url, obj, headers, 'PUT')


def deleteJsonObj(url, obj, headers):
    """ deletes object from url. Returns None if fails.
    """
    return jsonREST(url, obj, headers, 'DELETE')


def writeJsonObj(o, fn):
    """ Write an object to file fn in json safely
    Return True if successful else False
    """
    for i in range(5):
        try:
            f = open(fn, 'w')
        except OSError:
            logger.warn('unable to open %f for writing. %d' % (fn, i))
    if i == 5:
        logger.error('unable to open %f for writing.' % (fn))
        return False
    json.dump(o, f)
    f.close()
    return True
