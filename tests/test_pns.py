# -*- coding: utf-8 -*-
import sys
import base64
from urllib.request import pathname2url
import requests
import os

from .logdict import doLogging, logdict
if doLogging:
    import logging
    import logging.config
    # create logger
    logging.config.dictConfig(logdict)
    logger = logging.getLogger()
    logger.debug('level %d' % (logger.getEffectiveLevel()))
    logging.getLogger("requests").setLevel(logging.INFO)

from pns.common import getJsonObj, postJsonObj, putJsonObj, commonheaders
from pns.options import opt

# default configuration is provided. Copy pnsconfig.py to ~/local.py
from pns.pnsconfig import pnsconfig as pc
import sys
from os.path import expanduser, expandvars
env = expanduser(expandvars('$HOME'))
sys.path.insert(0, env)
try:
    from local import pnsconfig as pc
except Exception:
    pass

from pns import server
from dataset.odict import ODict
from dataset.serializable import serializeClassID, serializeClassID
from dataset.product import Product
from dataset.metadata import NumericParameter
from dataset.deserialize import deserializeClassID
from dataset.dataset import ArrayDataset, GenericDataset
from dataset.eq import deepcmp

testname = 'SVOM'
aburl = 'http://' + pc['node']['host'] + ':' + \
    str(pc['node']['port']) + pc['baseurl']

up = bytes((pc['node']['username'] + ':' +
            pc['node']['password']).encode('ascii'))
code = base64.b64encode(up).decode("ascii")
commonheaders.update({'Authorization': 'Basic %s' % (code)})
del up, code

# last timestamp/lastUpdate
lupd = 0


if 0:
    poststr = 'curl -i -H "Content-Type: application/json" -X POST --data @%s http://localhost:5000%s --user %s'
    cmd = poststr % ('resource/' + 'nodetestinput.jsn',
                     pathname2url(pc['baseurl'] + '/' +
                                  nodetestinput['creator'] + '/' +
                                  nodetestinput['rootcause']),
                     'foo:bar')
    print(cmd)
    os.system(cmd)
    sys.exit()


def checkserver():
    """ make sure the server is running when tests start
    """
    global testpns
    # check if data already exists
    o = getJsonObj(aburl + '/')
    assert o is not None, 'Cannot connect to the server'
    logger.info('initial server response %s' % (str(o)[:100] + '...'))
    # assert 'result' is not None, 'please start the server to refresh.'
    # initialize test data.


def checkputinitresult(result, msg):
    # if msg is string, an exception must have happened
    assert not isinstance(msg, (str, bytes)), msg
    assert result == 0, 'Error %d testing script file hello. STDOUT %s STDERR %s'\
        % (msg['returncode'], msg['stdout'], msg['stderr'])


def test_serverinit():
    """ server unit test for put init """
    ret, sta = server.initPTS(None)
    checkputinitresult(ret, sta)


def test_putinit():
    """ calls the default pnsconfig['scripts']['init'] script
    which checks the existence of 'hello'
    """

    d = {'timeout': 5}
    # print(nodetestinput)
    o = putJsonObj(aburl +
                   '/init',
                   d,
                   headers=commonheaders)
    issane(o)
    checkputinitresult(o['result'], o['message'])


def checkContents(cmd, filename):
    """ checks a GET commands return matches contents of a file.
    """
    o = getJsonObj(aburl + cmd)
    issane(o)
    with open(filename, 'r') as f:
        result = f.read()
    assert result == o['result'], o['message']


def test_putinittest():
    """ 
     Renames the 'prog' script to "*.save" and points it to the "hello" script.
    """

    d = {'timeout': 5}
    # print(nodetestinput)
    o = putJsonObj(aburl +
                   '/inittest',
                   d,
                   headers=commonheaders)
    issane(o)
    checkputinitresult(o['result'], o['message'])
    checkContents('/prog', pc['paths']['pnshome'] + '/hello')


def test_putconfigpns():
    """ send signatured pnsconfig and check.
    this function is useless for a stateless server
    """
    t = pc.copy()
    t['scripts']['testing'] = 'yes'
    d = {'timeout': 5, 'input': t}
    # print(nodetestinput)
    o = putJsonObj(aburl +
                   '/pnsconf',
                   d,
                   headers=commonheaders)
    issane(o)
    assert o['result']['scripts']['testing'] == 'yes', o['message']


def issane(o):
    """ basic check on POST return """
    global lupd
    assert o is not None, "Server is having trouble"
    assert 'error' not in o, o['error']
    assert o['timestamp'] > lupd
    lupd = o['timestamp']


def makeposttestdata():
    a1 = 'a test NumericParameter'
    a2 = 1
    a3 = 'second'
    v = NumericParameter(description=a1, value=a2, unit=a3)
    i0 = 6
    i1 = [[1, 2, 3], [4, 5, i0], [7, 8, 9]]
    i2 = 'ev'                 # unit
    i3 = 'img1'  # description
    image = ArrayDataset(data=i1, unit=i2, description=i3)
    x = Product(description="test post input product")
    x.set('testdataset', image)
    x.meta['testparam'] = v
    return ODict({'creator': 'me', 'rootcause': 'server test',
                  'input': x})


def checkpostresult(o):
    global lupd, nodetestinput
    p = o['result']
    assert issubclass(p.__class__, Product), (p.__class__)
    # creator rootcause
    # print('p.toString()' + p.toString())
    assert p.meta['creator'] == nodetestinput['creator']
    assert p.rootCause == nodetestinput['rootcause']
    # input data
    input = nodetestinput['input']
    pname, pv = list(input.meta.items())[0]
    dname, dv = list(input.getDataWrappers().items())[0]
    # compare with returened data
    assert p.meta[pname] == pv
    assert p[dname] == dv


def test_post():
    ''' send a set of data to the server and get back a product with
    properties, parameters, and dataset containing those in the input
    '''
    logger.info('POST testpipeline node server')
    global lupd, nodetestinput
    checkserver()
    nodetestinput = makeposttestdata()
    # print(nodetestinput)
    o = putJsonObj(aburl +
                   '/inittest',
                   None,
                   headers=commonheaders)
    o = postJsonObj(aburl +
                    '/testcalc',
                    nodetestinput,
                    headers=commonheaders)
    issane(o)
    checkpostresult(o)


def makeruntestdata():
    """ the input has only one product, which has one dataset,
    which has one data item -- a string that is the name
    """
    x = Product(description="hello world pipeline input product")
    x['theName'] = GenericDataset(
        data='stranger', description='input. the name')
    return x


def checkrunresult(p, msg):
    global lupd, nodetestinput

    if not issubclass(p.__class__, Product):
        assert issubclass(msg.__class__, str), str(p.__class__) + ' ' +\
            'Error %d running prog. STDOUT %s STDERR %s'\
            % (msg['returncode'], msg['stdout'], msg['stderr'])
        # Exception has happened.
        assert False, msg

    # creator rootcause
    # print('p.toString()' + p.toString())
    assert p.meta['creator'] == nodetestinput['creator']
    assert p.rootCause == nodetestinput['rootcause']
    # input data
    input = nodetestinput['input']
    answer = 'hello ' + input['theName'].data + '!\n'
    assert p['theAnswer'].data == answer


def test_serverrun():
    ''' send a product that has a name string as its data
    to the server "testrun" routine locally installed with this
    test, and get back a product with
    a string 'hello, $name!' as its data
    '''
    logger.info('POST test for pipeline node server "testrun": hello')
    global nodetestinput

    pi = server.checkpath(pc['paths']['inputdir'])
    po = server.checkpath(pc['paths']['outputdir'])
    assert pi is not None and po is not None

    x = makeruntestdata()
    # construct the nodetestinput to the node
    nodetestinput = ODict({'creator': 'me', 'rootcause': 'server test',
                           'input': x})
    js = serializeClassID(nodetestinput)
    logger.debug(js[:160])
    o, msg = server.testrun(js)
    # issane(o) is skipped
    checkrunresult(o, msg)


def test_run():
    ''' send a product that has a name string as its data
    to the server and get back a product with
    a string 'hello, $name!' as its data
    '''
    logger.info('POST test for pipeline node server: hello')
    global lupd, nodetestinput
    checkserver()

    test_putinit()

    x = makeruntestdata()
    # construct the nodetestinput to the node
    nodetestinput = ODict({'creator': 'me', 'rootcause': 'server test',
                           'input': x})
    # print(nodetestinput)
    o = postJsonObj(aburl +
                    '/testrun',
                    nodetestinput,
                    headers=commonheaders)
    issane(o)
    checkrunresult(o['result'], o['message'])


def test_getinit():
    ''' compare. server side initPTS contens with the local copy
    '''
    logger.info('get initPTS')
    checkContents(cmd='/init', filename=pc['scripts']['init'][0])


def test_getprog():
    ''' compare. server side prog contens with the local copy
    '''
    logger.info('get prog')
    checkContents(cmd='/prog', filename=pc['scripts']['prog'][0])


def test_deleteclean():
    ''' make input and output dirs and see if DELETE removes them.
    '''
    logger.info('delete cleanPTS')
    # make sure input and output dirs are made
    test_run()
    o = getJsonObj(aburl + '/input')
    issane(o)
    assert o['result'] is not None
    o = getJsonObj(aburl + '/output')
    issane(o)
    assert o['result'] is not None

    url = aburl + '/clean'
    try:
        r = requests.delete(url, headers=commonheaders, timeout=15)
        stri = r.text
        o = deserializeClassID(stri, dglobals=globals())
    except Exception as e:
        logger.debug(e)
        logger.error("Give up DELETE " + url)
        o = None
    issane(o)
    assert o['result'] is not None, o['message']
    o = getJsonObj(aburl + '/input')
    issane(o)
    assert o['result'] is None
    o = getJsonObj(aburl + '/output')
    issane(o)
    assert o['result'] is None


def test_mirror():
    ''' send a set of data to the server and get back the same.
    '''
    logger.info('POST testpipeline node server')
    checkserver()
    global lupd, nodetestinput
    nodetestinput = makeposttestdata()
    # print(nodetestinput)
    o = postJsonObj(aburl +
                    '/echo',
                    nodetestinput,
                    headers=commonheaders)
    # print(o)
    issane(o)
    r = deepcmp(o['result'], nodetestinput)
    assert r is None, r


if __name__ == '__main__':
    node, verbose = opt(node)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info('logging level %d' % (logger.getEffectiveLevel()))
    test_post()
    # test_getlastUpdate()
    # test_get()
    # test_get()
    test_postmirror()
    test_run()
    print('test successful')
