# -*- coding: utf-8 -*-
import pytest
from fdi.dataset.eq import deepcmp
from fdi.dataset.dataset import ArrayDataset, GenericDataset
from fdi.dataset.serializable import serializeClassID
from fdi.dataset.deserialize import deserializeClassID
from fdi.dataset.metadata import NumericParameter
from fdi.dataset.product import Product
from fdi.dataset.serializable import serializeClassID, serializeClassID
from fdi.dataset.odict import ODict
from fdi.utils.getconfig import getConfig
from fdi.utils.common import trbk
from fdi.pns import httppool_server as server
import sys
import base64
from urllib.request import pathname2url
from requests.auth import HTTPBasicAuth
import requests
import random
import os
import pkg_resources
import copy
import time
import getpass

import asyncio
import aiohttp

from fdi.pns.jsonio import getJsonObj, postJsonObj, putJsonObj, commonheaders
from fdi.utils.options import opt

# default configuration is provided. Copy pnsconfig.py to ~/local.py
from fdi.pns.pnsconfig import pnsconfig as pc


def setuplogging():
    import logging.config
    import logging
    from . import logdict

    # create logger
    logging.config.dictConfig(logdict.logdict)
    logging.getLogger("requests").setLevel(logging.WARN)
    logging.getLogger("urllib3").setLevel(logging.WARN)
    logging.getLogger("filelock").setLevel(logging.WARN)
    return logging


logging = setuplogging()
logger = logging.getLogger(__name__)


pc.update(getConfig())
logger.setLevel(pc['logginglevel'])
logger.debug('logging level %d' % (logger.getEffectiveLevel()))


if 0:
    @pytest.fixture(scope="module")
    def runserver():
        from fdi.pns.httppool_server import app
        app.run(host='127.0.0.1', port=5000,
                threaded=False, debug=verbose, processes=5)

        return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)


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

api_baseurl = pc['poolprefix'] + pc['baseurl'] + '/'
auth_user = pc['auth_user']
auth_pass = pc['auth_pass']
post_poolid = 'post_test_pool'
test_poolid = 'pool_default'
basepath = pc['server_poolpath']
prodt = 'fdi.dataset.product.Product'


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


def issane(o):
    """ basic check on return """
    global lupd
    assert o is not None, "Server is having trouble"
    assert 'error' not in o, o['error']
    assert o['timestamp'] > lupd
    lupd = o['timestamp']


def check0result(result, msg):
    # if msg is string, an exception must have happened
    assert result == 0, 'Error %d testing script "run". msg: ' + str(msg)
    assert msg == '' or not isinstance(msg, (str, bytes)), msg


def est_getpnspoolconfig():
    ''' gets and compares pnspoolconfig remote and local
    '''
    logger.info('get pnsconfig')
    o = getJsonObj(aburl + '/pnsconfig')
    issane(o)
    r = o['result']
    # , deepcmp(r['scripts'], pc['scripts'])
    assert r['scripts'] == pc['scripts']
    return r


def checkContents(cmd, filename):
    """ checks a GET commands return matches contents of a file.
    """
    o = getJsonObj(aburl + cmd)
    issane(o)
    with open(filename, 'r') as f:
        result = f.read()
    assert result == o['result'], o['message']


# TEST HTTPPOOL  API


def check_response(o, failed_case=False):
    global lupd
    assert o is not None, "Server is having trouble"
    if not failed_case:
        assert 'FAILED' != o['result'], o['result']
        assert o['timestamp'] > lupd
        lupd = o['timestamp']
    else:
        assert 'FAILED' == o['result'], o['result']


def clear_server_poolpath(poolid):
    """ deletes files in the given poolid in server pool dir. """
    logger.info('clear server pool dir ' + poolid)
    path = os.path.join(basepath, poolid)
    if os.path.exists(path):
        if path == '/':
            raise ValueError('cannot delete root')
        else:
            os.system('rm -rf ' + path)
        # x = Product(description='desc test case')
        # x.creator = 'test'
        # data = serializeClassID(x)
        # url = api_baseurl + test_poolid + '/fdi.dataset.product.Product/0'
        # x = requests.post(url, auth=HTTPBasicAuth(auth_user, auth_pass), data=data)


def get_files(poolid):
    """ returns a list of files in the given poolid in server pool dir. """

    path = os.path.join(basepath, poolid)
    if os.path.exists(path):
        files = os.listdir(path)
    else:
        files = []
    return files


def test_clear_server():
    clrpool = 'test_clear'
    cpath = os.path.join(basepath, clrpool)
    if not os.path.exists(cpath):
        os.mkdir(cpath)
    assert os.path.exists(cpath)
    with open(cpath+'/foo', 'w') as f:
        f.write('k')
    clear_server_poolpath(clrpool)
    assert not os.path.exists(cpath)


def populate_server(poolid):
    creators = ['Todds', 'Cassandra', 'Jane', 'Owen', 'Julian', 'Maurice']
    instruments = ['fatman', 'herscherl', 'NASA', 'CNSC', 'SVOM']
    for index, i in enumerate(creators):
        x = Product(description='desc ' + str(index),
                    instrument=random.choice(instruments))
        x.creator = i
        data = serializeClassID(x)
        url = api_baseurl + poolid + '/' + prodt + '/' + str(index)
        x = requests.post(url, auth=HTTPBasicAuth(
            auth_user, auth_pass), data=data)
        o = deserializeClassID(x.text)
        check_response(o)
    return creators, instruments


def test_CRUD_product():
    ''' test saving, read, delete products API, products will be saved at /data/pool_id
    '''
    logger.info('save products')
    clear_server_poolpath(post_poolid)

    files = get_files(post_poolid)
    origin_prod = sum(1 for f in files if f[-1].isnumeric())
    creators, instruments = populate_server(post_poolid)
    files = get_files(post_poolid)

    num_prod = sum(1 for f in files if f[-1].isnumeric())
    assert num_prod == len(creators) + origin_prod, 'Products number not match'

    # ==========
    logger.info('read product')
    index = random.choice(range(origin_prod, num_prod))
    prodpath = '/' + prodt + '/' + str(index)
    url = api_baseurl + post_poolid + prodpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)
    assert o['result'].creator == creators[index -
                                           origin_prod], 'Creator not match'

    # ===========
    ''' Test read hk api
    '''
    logger.info('read hk')
    hkpath = '/hk'
    url = api_baseurl + post_poolid + hkpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)
    assert o['result']['classes'] is not None, 'Classes jsn read failed'
    assert o['result']['tags'] is not None, 'Tags jsn read failed'
    assert o['result']['urns'] is not None, 'Urns jsn read failed'

    assert o['result']['classes'][prodt]['sn'] == list(range(len(creators)))
    assert o['result']['classes'][prodt]['currentSN'] == len(creators) - 1
    assert len(o['result']['tags']) == 0
    assert [d['meta']['creator'].value for u,
            d in o['result']['urns'].items()] == creators

    logger.info('read classes')
    hkpath = '/hk/classes'
    url = api_baseurl + post_poolid + hkpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)
    assert o['result'][prodt]['sn'] == list(range(len(creators)))
    assert o['result'][prodt]['currentSN'] == len(creators) - 1

    logger.info('read tags')
    hkpath = '/hk/tags'
    url = api_baseurl + post_poolid + hkpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)
    assert len(o['result']) == 0

    logger.info('read urns')
    hkpath = '/hk/urns'
    url = api_baseurl + post_poolid + hkpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)

    clst = [d['meta']['creator'].value for u, d in o['result'].items()]
    assert clst == creators

    # ========
    logger.info('delete a product')
    files = get_files(post_poolid)
    fps = [f for f in files if f[-1].isnumeric()]
    origin_prod = len(fps)
    index = fps[-1].rsplit('_', 1)[1]
    url = api_baseurl + post_poolid + '/fdi.dataset.product.Product/' + index
    x = requests.delete(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)
    files = get_files(post_poolid)
    num_prod = sum(1 for f in files if f[-1].isnumeric())
    assert num_prod + 1 == origin_prod, 'Remove product failed'

    # ========
    logger.info('delete a pool')
    files = get_files(post_poolid)
    assert len(files) != 0, 'Pool is already empty: ' + post_poolid

    url = api_baseurl + post_poolid
    x = requests.delete(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o)

    files = get_files(post_poolid)
    assert len(files) == 0, 'Wipe pool failed: ' + o['msg']


async def lock_pool(poolid, sec):
    ''' Lock a pool and return a fake response
    '''
    import filelock
    import time
    logger.info('Keeping files locked')
    ppath = os.path.join(basepath, poolid)
    with filelock.FileLock('/tmp/fdi_locks/' + ppath.replace('/', '_')):
        await asyncio.sleep(sec)
    fakeres = '{"result": "FAILED", "msg": "This is a fake responses", "timestamp": ' + \
        str(time.time()) + '}'
    return deserializeClassID(fakeres)


async def read_product(poolid):
    prodpath = '/'+prodt+'/0'
    url = api_baseurl + poolid + prodpath
    logger.info('Read a locked file')
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=aiohttp.BasicAuth(auth_user, auth_pass)) as res:
            x = await res.text()
            o = deserializeClassID(x)
    logger.info(x)
    return o


def test_lock_file():
    ''' Test if a pool is locked, others can not manipulate this pool anymore before it's released
    '''
    logger.info('Test read a locked file, it will return FAILED')
    poolid = test_poolid
    populate_server(poolid)
    try:
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(
            lock_pool(poolid, pc['timeout']+1)), asyncio.ensure_future(read_product(poolid))]
        taskres = loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        res = [f.result() for f in [x for x in taskres][0]]
        check_response(res[0], True)
        check_response(res[1], True)
    except Exception as e:
        print('Error: unable to start thread ' + str(e))
        raise e


def test_read_non_exists_pool():
    ''' Test read a pool which doesn't exist, returns FAILED
    '''
    logger.info('Test query a pool non exist.')
    wrong_poolid = 'abc'
    prodpath = '/' + prodt + '/0'
    url = api_baseurl + wrong_poolid + prodpath
    x = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass))
    o = deserializeClassID(x.text)
    check_response(o, True)


def test_subclasses_pool():
    logger.info('Test create a pool which has subclass')
    poolid_1 = 'subclasses/a'
    poolid_2 = 'subclasses/b'
    prodpath = '/' + prodt + '/0'
    url1 = api_baseurl + poolid_1 + prodpath
    url2 = api_baseurl + poolid_2 + prodpath
    x = Product(description="product example with several datasets",
                instrument="Crystal-Ball", modelName="Mk II")
    data = serializeClassID(x)
    res1 = requests.post(url1, auth=HTTPBasicAuth(
        auth_user, auth_pass), data=data)
    res2 = requests.post(url2, auth=HTTPBasicAuth(
        auth_user, auth_pass), data=data)
    o1 = deserializeClassID(res1.text)
    o2 = deserializeClassID(res2.text)
    check_response(o1)
    check_response(o2)

    # Wipe these pools
    url1 = api_baseurl + poolid_1
    url2 = api_baseurl + poolid_2

    res1 = requests.delete(url1,  auth=HTTPBasicAuth(auth_user, auth_pass))
    res2 = requests.delete(url2,  auth=HTTPBasicAuth(auth_user, auth_pass))
    o1 = deserializeClassID(res1.text)
    check_response(o1)
    o2 = deserializeClassID(res2.text)
    check_response(o2)

# ##################################

# def test_putconfigpns():
#     """ send signatured pnsconfig and check.
#     this function is useless for a stateless server
#     """
#     t = test_getpnsconfig()
#     t['testing'] = 'yes'
#     d = {'timeout': 5, 'input': t}
#     # print(nodetestinput)
#     o = putJsonObj(aburl +
#                    '/pnsconf',
#                    d,
#                    headers=commonheaders)
#     # put it back not to infere other tests
#     del t['testing']
#     d = {'timeout': 5, 'input': t}
#     p = putJsonObj(aburl +
#                    '/pnsconf',
#                    d,
#                    headers=commonheaders)
#
#     issane(o)
#     assert o['result']['testing'] == 'yes', o['message']
#     assert 'testing' not in pc, str(pc)
#     issane(p)
#     assert 'testing' not in p['result']


# def makeposttestdata():
#     a1 = 'a test NumericParameter'
#     a2 = 1
#     a3 = 'second'
#     v = NumericParameter(description=a1, value=a2, unit=a3)
#     i0 = 6
#     i1 = [[1, 2, 3], [4, 5, i0], [7, 8, 9]]
#     i2 = 'ev'                 # unit
#     i3 = 'img1'  # description
#     image = ArrayDataset(data=i1, unit=i2, description=i3)
#     x = Product(description="test post input product")
#     x.set('testdataset', image)
#     x.meta['testparam'] = v
#     return ODict({'creator': 'me', 'rootcause': 'server test',
#                   'input': x})
#
#
# def checkpostresult(o, nodetestinput):
#
#     p = o['result']
#     assert issubclass(p.__class__, Product), (p.__class__)
#     # creator rootcause
#     # print('p.toString()' + p.toString())
#     assert p.meta['creator'] == nodetestinput['creator']
#     assert p.rootCause == nodetestinput['rootcause']
#     # input data
#     input = nodetestinput['input']
#     pname, pv = list(input.meta.items())[0]
#     dname, dv = list(input.getDataWrappers().items())[0]
#     # compare with returened data
#     assert p.meta[pname] == pv
#     assert p[dname] == dv
#
#
# def test_post():
#     ''' send a set of data to the server and get back a product with
#     properties, parameters, and dataset containing those in the input
#     '''
#     logger.info('POST testpipeline node server')
#
#     nodetestinput = makeposttestdata()
#     # print(nodetestinput)
#     o = postJsonObj(aburl +
#                     '/testcalc',
#                     nodetestinput,
#                     headers=commonheaders)
#     issane(o)
#     checkpostresult(o, nodetestinput)
#
#
# def makeruntestdata():
#     """ the input has only one product, which has one dataset,
#     which has one data item -- a string that is the name
#     """
#     x = Product(description="hello world pipeline input product")
#     x['theName'] = GenericDataset(
#         data='stranger', description='input. the name')
#     return x
#
#
# def checkrunresult(p, msg, nodetestinput):
#
#     assert issubclass(p.__class__, Product), str(p) + ' ' + str(msg)
#
#     # creator rootcause
#     # print('p.toString()' + p.toString())
#     assert p.meta['creator'] == nodetestinput['creator']
#     assert p.rootCause == nodetestinput['rootcause']
#     # input data
#     input = nodetestinput['input']
#     answer = 'hello ' + input['theName'].data + '!'
#     assert p['theAnswer'].data[:len(answer)] == answer
#
#
# def test_servertestrun():
#     ''' send a product that has a name string as its data
#     to the server "testrun" routine locally installed with this
#     test, and get back a product with
#     a string 'hello, $name!' as its data
#     '''
#     logger.info('POST test for pipeline node server "testrun": hello')
#
#     test_servertestinit()
#
#     x = makeruntestdata()
#     # construct the nodetestinput to the node
#     nodetestinput = ODict({'creator': 'me', 'rootcause': 'server test',
#                            'input': x})
#     js = serializeClassID(nodetestinput)
#     logger.debug(js[:160])
#     o, msg = server.testrun(js)
#     # issane(o) is skipped
#     checkrunresult(o, msg, nodetestinput)
#
#
# def test_testrun():
#     ''' send a product that has a name string as its data
#     to the server and get back a product with
#     a string 'hello, $name!' as its data
#     '''
#     logger.info('POST test for pipeline node server: hello')
#
#     test_puttestinit()
#
#     x = makeruntestdata()
#     # construct the nodetestinput to the node
#     nodetestinput = ODict({'creator': 'me', 'rootcause': 'server test',
#                            'input': x})
#     # print(nodetestinput)
#     o = postJsonObj(aburl +
#                     '/testrun',
#                     nodetestinput,
#                     headers=commonheaders)
#     issane(o)
#     checkrunresult(o['result'], o['message'], nodetestinput)
#
#
# def test_deleteclean():
#     ''' make input and output dirs and see if DELETE removes them.
#     '''
#     logger.info('delete cleanPTS')
#     # make sure input and output dirs are made
#     test_testrun()
#     o = getJsonObj(aburl + '/input')
#     issane(o)
#     assert o['result'] is not None
#     o = getJsonObj(aburl + '/output')
#     issane(o)
#     assert o['result'] is not None
#
#     url = aburl + '/clean'
#     try:
#         r = requests.delete(url, headers=commonheaders, timeout=15)
#         stri = r.text
#     except Exception as e:
#         logger.error("Give up DELETE " + url + ' ' + str(e))
#         stri = None
#     o = deserializeClassID(stri)
#     issane(o)
#     assert o['result'] is not None, o['message']
#     o = getJsonObj(aburl + '/input')
#     issane(o)
#     assert o['result'] is None
#     o = getJsonObj(aburl + '/output')
#     issane(o)
#     assert o['result'] is None
#
#
# def test_mirror():
#     ''' send a set of data to the server and get back the same.
#     '''
#     logger.info('POST testpipeline node server')
#     nodetestinput = makeposttestdata()
#     # print(nodetestinput)
#     o = postJsonObj(aburl +
#                     '/echo',
#                     nodetestinput,
#                     headers=commonheaders)
#     # print(o)
#     issane(o)
#     r = deepcmp(o['result'], nodetestinput)
#     assert r is None, r
#
#
# def test_serversleep():
#     """
#     """
#     s = '1.5'
#     tout = 2
#     now = time.time()
#     re, st = server.dosleep({'timeout': tout}, s)
#     d = time.time() - now - float(s)
#     assert re == 0, str(re)
#     assert d > 0 and d < 0.5
#     print('dt=%f re=%s state=%s' % (d, str(re), str(st)))
#     now = time.time()
#     # let it timeout
#     tout = 1
#     re, st = server.dosleep({'timeout': tout}, s)
#     d = time.time() - now - tout
#     assert re < 0
#     assert d > 0 and d < float(s) - tout
#     print('dt=%f re=%s state=%s' % (d, str(re), str(st)))
#
#
# def test_sleep():
#     """
#     """
#     s = '1.5'
#     tout = 2
#     now = time.time()
#     o = postJsonObj(aburl +
#                     '/sleep/' + s,
#                     {'timeout': tout},
#                     headers=commonheaders)
#     d = time.time() - now - float(s)
#     # print(o)
#     issane(o)
#     re, st = o['result'], o['message']
#     assert re == 0, str(re)
#     assert d > 0 and d < 0.5
#     #print('deviation=%f re=%s state=%s' % (d, str(re), str(st)))
#     # let it timeout
#     tout = 1
#     now = time.time()
#     o = postJsonObj(aburl +
#                     '/sleep/' + s,
#                     {'timeout': tout},
#                     headers=commonheaders)
#     d = time.time() - now - tout
#     # print(o)
#     issane(o)
#     re, st = o['result'], o['message']
#     assert re < 0
#     assert d > 0 and d < float(s) - tout
#     #print('deviation=%f re=%s state=%s' % (d, str(re), str(st)))
#
#
# from multiprocessing import Process, Pool, TimeoutError
#
#
# def info(title):
#     print(title)
#     print('module name:' + __name__)
#     if hasattr(os, 'getppid'):  # only available on Unix
#         print('parent process: %d' % (os.getppid()))
#     print('process id: ' + str(os.getpid()))
#     print(time.time())
#
#
# def nap(t, d):
#     info(t)
#     time.sleep(d)
#     s = str(t)
#     tout = 5
#     o = postJsonObj(aburl +
#                     '/sleep/' + s,
#                     {'timeout': tout},
#                     headers=commonheaders
#                     )
#     # print('nap ' + str(time.time()) + ' ' + str(s) + ' ' + str(o)
#     return o
#
#
# import aiohttp
# import asyncio
#
#
# async def napa(t, d):
#     # info(t)
#     asyncio.sleep(d)
#     s = str(t)
#     tout = 11
#     o = None
#     js = serializeClassID({'timeout': tout})
#     async with aiohttp.ClientSession() as session:
#         async with session.post(aburl +
#                                 '/sleep/' + s,
#                                 data=js,
#                                 headers=commonheaders
#                                 ) as resp:
#             # print(resp.status)
#             stri = await resp.text()
#     o = deserializeClassID(stri)
#     #print('nap ' + str(time.time()) + ' ' + str(s) + ' ' + str(o))
#     return o
#
#
# def test_lock():
#     """ when a pns is busy with any commands that involves executing in the $pnshome dir the execution is locked system-wide with a lock-file .lock. Any attempts to execute a shell command when the lock is in effect will get a 409.
#     """
#
#     tm = 3
#     if 0:
#         with Pool(processes=4) as pool:
#             res = pool.starmap(nap, [(tm, 0), (0.5, 0.5)])
#     if 0:
#         # does not work
#         import threading
#         try:
#             threading.Thread(target=nap(tm, 0))
#             threading.Thread(target=nap(0.5, 0.5))
#         except Exception as e:
#             print("Error: unable to start thread " + str(e))
#         time.sleep(tm + 2)
#     if 1:
#         asyncio.set_event_loop(asyncio.new_event_loop())
#         loop = asyncio.get_event_loop()
#         tasks = [asyncio.ensure_future(napa(tm, 0)),
#                  asyncio.ensure_future(napa(0.5, 0.5))]
#         taskres = loop.run_until_complete(asyncio.wait(tasks))
#         loop.close()
#         res = [f.result() for f in [x for x in taskres][0]]
#
#     # print(res)
#     if issubclass(res[0]['message'].__class__, ODict):
#         r1, r2 = res[0], res[1]
#     else:
#         r2, r1 = res[0], res[1]
#     assert r1['result'] == 0
#     assert '409' in r2['message']


if __name__ == '__main__':
    now = time.time()
    node, verbose = opt(pc['node'])
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info('logging level %d' % (logger.getEffectiveLevel()))

    t = 8

    if t == 7:
        # test_lock()
        # asyncio.AbstractEventLoop.set_debug()
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(napa(5, 0)),
                 asyncio.ensure_future(napa(0.5, 0.5))]
        res = loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        print(res)

    elif t == 3:
        # test_getpnsconfig()
        test_puttestinit()
        test_putinit()
        test_getinit()
        test_getrun()
        test_putconfigpns()
        test_post()
        test_testrun()
        test_deleteclean()
        test_mirror()
        test_sleep()
    elif t == 4:
        test_serverinit()
        test_servertestinit()
        test_servertestrun()
        test_serversleep()
    elif t == 6:
        test_vvpp()

    print('test successful ' + str(time.time() - now))
