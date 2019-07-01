import os
import errno
from pprint import pprint, pformat
# import urllib2
import urllib.request
import urllib.error as ue
import json
import getopt
import sys

from pns.logdict import logdict
import logging
import logging.config
# create logger
logging.config.dictConfig(logdict)
logger = logging.getLogger(__name__)
logger.debug('level %d' % (logger.getEffectiveLevel()))


if 0:
    print(logger.propagate)
    print(logger.disabled)
    print(logger.filters)
    print(logger.hasHandlers())
    print(logger.handlers)
    print(logger.level)

from dataset.deserialize import deserializeClassID
from dataset.eq import serializeClassID

commonheaders = {
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8',
    'Accept-Encoding': 'identity',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    "Content-type": 'application/json'
}


class Decoder(json.JSONDecoder):
    """ adapted from https://stackoverflow.com/questions/45068797/how-to-convert-string-int-json-into-real-int-with-json-loads
    modified to also convert keys in dictionaries.
    """

    def decode(self, s):
        result = super().decode(s)  # result = super(Decoder, self).decode(s) for Python 2.x
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o, str) or isinstance(o, bytes):
            try:
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {self._decode(k): self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o


def getJsonObj(url, headers=None):
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
            # python 2
            # stri = urllib2.urlopen(urllib2.Request(url), timeout=15).read()
            # python3
            stri = urllib.request.urlopen(
                url, timeout=15).read().decode('utf-8')
            #logger.debug('stri ' + stri)
            break
        except Exception as e:
            logger.debug(e)
            if issubclass(e.__class__, ue.HTTPError):
                ret = e
                return None
            if i >= 5:
                logger.error("Give up " + url + " after %d tries." % i)
                return None
            else:
                i += 1
    # print(url,stri)
    # ret = json.loads(stri, parse_float=Decimal)
    # ret = json.loads(stri, cls=Decoder,
    #               object_pairs_hook=collections.OrderedDict)
    ret = deserializeClassID(stri)
    logger.debug(pformat(ret, depth=6)[:160] + '...')
    return ret


import requests
from http.client import HTTPConnection
# HTTPConnection.debuglevel = 1


def postJsonObj(url, obj, headers):
    """ posts object to url. Returns None if fails.
    """
    js = serializeClassID(obj)
    # %s obj %s headers %s' % (url, obj, headers))
    logger.debug(url + js[:160])

    i = 1
    while True:
        try:
            # python3
            r = requests.post(url, data=js, headers=headers, timeout=15)
            stri = r.text
            # print('ps textx %s\nstatus %d\nheader %s' % (stri, r.status_code, r.headers))
            break
        except Exception as e:
            logger.debug(e)
            if i >= 1:
                logger.error("Give up POST " + url + " after %d tries." % i)
                return None
            else:
                i += 1

    # ret = json.loads(stri, parse_float=Decimal)
    # ret = json.loads(stri, cls=Decoder)
    ret = deserializeClassID(stri)
    logger.debug(pformat(ret, depth=6)[:160] + '...')
    return ret


def putJsonObj(url, obj, headers):
    """ puts object to url. Returns None if fails.
    """
    js = serializeClassID(obj)
    # %s obj %s headers %s' % (url, obj, headers))
    logger.debug(url + js[:160])

    try:
        # python3
        r = requests.put(url, data=js, headers=headers, timeout=15)
        stri = r.text
    except Exception as e:
        logger.debug(e)
        logger.error("Give up PUT " + url)
        return None

    ret = deserializeClassID(stri)
    logger.debug(pformat(ret, depth=6)[:160] + '...')
    return ret


def postJsonObj2(url, obj, headers):
    """ post object to url. Return None if fail.
    """
    logger.debug('postJsonObj url %s obj %s headers %s' % (url, obj, headers))
    #
    data = urllib.parse.urlencode(obj).encode()
    # print('o', obj, 'd', data)
    i = 1
    while True:
        try:
             # python3
            req = urllib.request.Request(url, data=data, headers=headers)
            stri = urllib.request.urlopen(
                req, timeout=15).read().decode('utf-8')
            # ret = json.loads(stri, parse_float=Decimal)
            ret = json.loads(stri, cls=Decoder)
            break
        except Exception as e:
            print(e)
            if i >= 5:
                logger.error("Give up POST " + url + " after %d tries." % i)
                return None
            else:
                i += 1
    # print(url,stri)
    logger.debug(pformat(ret, depth=3)[:170] + '...')
    return ret


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


def addslash(path):
    """ add a slash at the end of path if there is not one.
    """
    logger.debug('%s' % (path))
    if path[-1] != '/':
        path += '/'
    return path


def mkdir(f, mode=0o755):
    """ mkdir for one or multi-level paths. ignore if dir exists.
    raise exception on other errors.
    """
    logger.debug('%s %o' % (f, mode))
    path = ''
    for i in f.split('/'):
        if i == '':
            continue
        path += (i + '/')
        loger.debug(path)
        try:
            os.mkdir(path, mode)
        except OSError as e:
            if e.errno == errno.EEXIST:  # file exists error?
                pass  # logger.info('%s exists' % (path))
            else:
                raise(e)  # re-raise the exception
            os.chmod(path, mode)


def opt(node):
    """Get username and password and host ip and port
    """

    logger.debug('username %s password %s host=%s port=%d' %
                 (node['username'], node['password'],
                  node['host'], node['port']))
    msg = 'Specify non-empty username (-u or --username=) and password (-p or --password= ) host IP (-i or --ip=) and port (-o or --port=) on commandline.'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:i:o:v",
                                   [
                                       "help",
                                       "username=",
                                       "password=",
                                       "ip=",
                                       "port=",
                                       'verbose'
        ])
    except getopt.GetoptError as err:
        # print help information and exit:
        # will print something like "option -a not recognized"
        logger.error(str(err))
        logger.info(msg)
        sys.exit(2)
    logger.debug('Command line options %s args %s' % (opts, args))
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", '--help'):
            print(msg)
            sys.exit(0)
        elif o in ("-u", '--username'):
            node['username'] = a
        elif o in ('-p', '--password'):
            node['password'] = a
        elif o in ("-i", '--ip'):
            node['host'] = a
        elif o in ('-o', '--port'):
            node['port'] = int(a)
        else:
            logger.error("unhandled option")
            print(msg)
            sys.exit(1)
    logger.debug('username %s password %s host=%s port=%d' %
                 (node['username'], node['password'],
                  node['host'], node['port']))
    return node, verbose


if 0 and __name__ == '__main__':
    test_readtable_volume()
