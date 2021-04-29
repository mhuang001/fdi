# -*- coding: utf-8 -*-


from ..utils.common import lls
from ..dataset.deserialize import deserialize
from ..dataset.serializable import serialize
from ..pal.poolmanager import PoolManager
from ..pal.query import MetaQuery, AbstractQuery
from ..pal.urn import makeUrn, parseUrn
from ..pal.webapi import WebAPI
from ..dataset.product import Product
from ..dataset.classes import Classes
from ..utils.common import fullname, trbk
from ..utils.fetch import fetch
# from .db_utils import check_and_create_fdi_record_table, save_action

# import mysql.connector
# from mysql.connector import Error

import sys
import os
import copy
import json
import time
import pprint
import builtins
from collections import ChainMap
from itertools import chain
import importlib
from flask import request, make_response, jsonify
from flask.wrappers import Response

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
    strset = str
    from urllib.parse import urlparse
else:
    PY3 = False
    # strset = (str, unicode)
    strset = str
    from urlparse import urlparse

# from .logdict import logdict
# '/var/log/pns-server.log'
# logdict['handlers']['file']['filename'] = '/tmp/server.log'

from .server_skeleton import init_conf_clas, makepublicAPI, logging, checkpath, app, auth, pc

logger = logging.getLogger(__name__)


# =============HTTP POOL=========================

# the httppool that is local to the server
schm = 'server'


@app.before_first_request
def init_httppool_server():
    """ Init a global HTTP POOL """
    global pc, Classes, PM, BASEURL, basepath, poolpath, pylookup

    Classes = init_conf_clas()
    lookup = ChainMap(Classes.mapping, globals(), vars(builtins))

    from ..pal.poolmanager import PoolManager as PM, DEFAULT_MEM_POOL
    if PM.isLoaded(DEFAULT_MEM_POOL):
        logger.debug('cleanup DEFAULT_MEM_POOL')
        PM.getPool(DEFAULT_MEM_POOL).removeAll()
    logger.debug('Done cleanup PoolManager.')
    logger.debug('ProcID %d 1st reg %s' % (os.getpid(),
                                           str(app._got_first_request))
                 )
    PM.removeAll()

    basepath = PM.PlacePaths[schm]
    poolpath = os.path.join(basepath, pc['api_version'])

    if checkpath(poolpath, pc['serveruser']) is None:
        logger.error('Store path %s unavailable.' % poolpath)
        sys.exit(-2)

   # load_all_pools()


def getallpools(path):
    alldirs = []
    allfilelist = os.listdir(path)
    for file in allfilelist:
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            alldirs.append(file)
    return alldirs


def load_all_pools():
    """
    Adding all pool to server pool storage.
    """
    alldirs = set()

    path = poolpath
    logger.debug('loading all from ' + path)

    alldirs = getallpools(path)
    for poolname in alldirs:
        poolurl = schm + '://' + os.path.join(poolpath, poolname)
        PM.getPool(poolname=poolname, poolurl=poolurl)
        logger.info("Registered pool: %s in %s" % (poolname, poolpath))


# Check database
# check_and_create_fdi_record_table()


@ app.route(pc['baseurl'], methods=['GET'])
@ app.route(pc['baseurl']+'/', methods=['GET'])
@ app.route(pc['baseurl']+'/pools', methods=['GET'])
def get_pools():
    ts = time.time()
    path = poolpath
    logger.debug('listing all from ' + path)

    result = serialize(getallpools(path))
    msg = 'pools found.'
    w = '{"result": %s, "msg": "%s", "timestamp": %f}' % (
        result, msg, ts)
    logger.debug(lls(w, 240))
    resp = make_response(w)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@ app.route(pc['baseurl'] + '/<string:cmd>', methods=['GET'])
def getinfo(cmd):
    ''' returns init, config, run input, run output.
    '''
    msg = ''
    ts = time.time()

    if cmd == 'config':
        p = copy.copy(pc)
        p['node']['username'], p['node']['password'] = '*', '*'
        p['auth_user'], p['auth_pass'] = '*', '*'
        result, msg = serialize(p), 'Getting configuration OK.'
    else:
        allpools = get_pools()
        if cmd in allpools:
            cls = load_single_HKdata([cmd, 'hk', 'classes'])
            result, msg = cls, 'Getting pool %s info OK'
        else:
            result, msg = '"FAILED"', cmd + ' is not valid.'

    w = '{"result": %s, "msg": "%s", "timestamp": %f}' % (
        result, msg, ts)
    logger.debug(lls(w, 240))
    resp = make_response(w)
    resp.headers['Content-Type'] = 'application/json'
    return resp

# @ app.route(pc['baseurl'] + '/sn' + '/<string:prod_type>' + '/<string:pool_id>', methods=['GET'])


def get_prod_count(prod_type, pool_id):
    """ Return the total count for the given product type and pool_id in the directory.

    'prod_type': 'clsssname',
    'pool_id': 'pool name'

    """

    logger.debug('### method %s prod_type %s poolID %s***' %
                 (request.method, prod_type, pool_id))
    res = 0
    nm = []
    path = os.path.join(poolpath, pool_id)
    if os.path.exists(path):
        for i in os.listdir(path):
            if i[-1].isnumeric() and prod_type in i:
                res = res+1
                nm.append(i)
    s = str(nm)
    logger.debug('found '+s)
    return str(res), 'Counting %s files OK'


@ app.route(pc['baseurl'] + '/<path:pool>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@ auth.login_required
def httppool(pool):
    """
    APIs for CRUD products, according to path and methods and return results.

    - GET:
                 /pool_id/product_class/index ==> return product
                 /pool_id/hk ===> return pool_id Housekeeping data; urns, classes, and tags
                 /pool_id/hk/{urns, classes, tags} ===> return pool_id urns or classes or tags
                 /pool_id/count/product_class ===> return the number of products in the pool

    - POST: /pool_id ==> Save product in requests.data in server

    - PUT: /pool_id ==> register pool

    - DELETE: /pool_id ==> unregister pool_id
                         /pool_id/product_class/index ==> remove specified products in pool_id

    'pool':'url'
    """
    username = request.authorization.username
    paths = pool.split('/')
    if paths[-1] == '':
        del paths[-1]

    lp = len(paths)
    ts = time.time()
    # do not deserialize if set True. save directly to disk
    serial_through = True
    logger.debug('*** method %s paths %s ***' % (request.method, paths))
    if 0 and paths[0] == 'testhttppool':
        import pdb
        pdb.set_trace()

    if request.method == 'GET':
        # TODO modify client loading pool , prefer use load_HKdata rather than load_single_HKdata, because this will generate enormal sql transaction
        if paths[1] == 'hk' and lp == 2:  # Load all HKdata
            result, msg = load_HKdata(paths)
            # save_action(username=username, action='READ', pool=paths[0])
        elif paths[1] == 'hk' and paths[2] in ['classes', 'urns', 'tags']:  # Retrieve single HKdata
            result, msg = load_single_HKdata(paths)
            # save_action(username=username, action='READ', pool=paths[0])
        elif paths[1] == 'count' and lp == 3:  # prod count
            result, msg = get_prod_count(paths[2], paths[0])
        elif paths[1] == 'api':
            result, msg = call_pool_Api(paths)
        elif lp > 1:
            result, msg = getProduct_Or_Component(
                paths, serialize_out=serial_through)
        elif 0:  # paths[-1].isnumeric():  # Retrieve product
            result, msg = load_product(1, paths, serialize_out=serial_through)
            # save_action(username=username, action='READ', pool=paths[0])

        else:
            result = '"FAILED"'
            msg = 'Unknown request: ' + pool

    elif request.method == 'POST' and paths[-1].isnumeric() and request.data != None:
        if request.headers.get('tag') is not None:
            tag = request.headers.get('tag')
        else:
            tag = None

        if serial_through:
            data = str(request.data, encoding='ascii')

            result, msg = save_product(
                data, paths, tag, serialize_in=not serial_through, serialize_out=serial_through)
        else:
            try:
                data = deserialize(request.data)
            except ValueError as e:
                result = '"FAILED"'
                msg = 'Class needs to be included in pool configuration.' + \
                    str(e) + ' ' + trbk(e)
            else:
                result, msg = save_product(
                    data, paths, tag, serialize_in=not serial_through)
                # save_action(username=username, action='SAVE', pool=paths[0])
    elif request.method == 'PUT':
        result, msg = register_pool(paths)

    elif request.method == 'DELETE':
        if paths[-1].isnumeric():
            result, msg = delete_product(paths)
            # save_action(username=username, action='DELETE', pool=paths[0] +  '/' + paths[-2] + ':' + paths[-1])
        else:
            result, msg = unregister_pool(paths)
            # save_action(username=username, action='DELETE', pool=paths[0])
    else:
        result, msg = '"FAILED"', 'UNknown command '+request.method

    if issubclass(result.__class__, Response):
        return result
    # w = {'result': result, 'msg': msg, 'timestamp': ts}
    # make a json string
    r = '"null"' if result is None else str(result)
    w = '{"result": %s, "msg": %s, "timestamp": %f}' % (
        r, json.dumps(msg), ts)
    # logger.debug(pprint.pformat(w, depth=3, indent=4))
    s = w  # serialize(w)
    logger.debug(lls(s, 240))
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


Builtins = vars(builtins)


def mkv(v, t):

    m = v if t == 'str' else None if t == 'NoneType' else Builtins[t](
        v) if t in Builtins else deserialize(v)
    return m


def call_pool_Api(paths):
    """ run api calls on the running pool.

    """
    # index of method name
    im = 2
    # remove empty trailing strings
    for o in range(len(paths), 1, -1):
        if paths[o-1]:
            break

    paths = paths[:o]
    lp = len(paths)
    method = paths[im]
    if method not in WebAPI:
        return '"FAILED"', 'Unknown web API method: %s.' % method
    args, kwds = [], {}

    if 0:
        poolname = paths[0]
        s = PM.isLoaded(poolname)
        import pdb
        pdb.set_trace()

    if lp > im:
        if (lp-im) % 2 == 0:
            # there are odd number of args+key+val
            try:
                tyargs = paths[im+1].split('|')
                args = []
                for a in tyargs:
                    s = a.rsplit(':', 1)
                    v, t = s[0], s[1]
                    args.append(mkv(v, t))
            except IndexError as e:
                result = '"FAILED"'
                msg = 'Bad arguement format ' + paths[im+1] + \
                    ' Exception: ' + str(e) + ' ' + trbk(e)
                logger.error(msg)
                return result, msg
            kwstart = im + 2
        else:
            kwstart = im + 1
        try:
            while kwstart < lp:
                s = paths[kwstart+1].rsplit(':', 1)
                v, t = s[0], s[1]
                kwds[paths[kwstart]] = mkv(v, t)
                kwstart += 2
        except IndexError as e:
            result = '"FAILED"'
            msg = 'Bad arguement format ' + paths[kwstart+1] + \
                ' Exception: ' + str(e) + ' ' + trbk(e)
            logger.error(msg)
            return result, msg
    kwdsexpr = (str(k)+'='+str(v) for k, v in kwds.items())
    msgexpr = '%s(%s)' % (method, ', '.join(chain(map(str, args), kwdsexpr)))
    logger.debug('WebAPI ' + msgexpr)

    poolname = paths[0]
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    if not PM.isLoaded(poolname):
        result = '"FAILED"'
        msg = 'Pool not found: ' + poolname
        logger.error(msg)
        return result, msg

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        res = getattr(poolobj, method)(*args, **kwds)
        result = serialize(res)
        msg = msgexpr + ' OK.'
    except Exception as e:
        result = '"FAILED"'
        msg = 'Unable to complete ' + msgexpr + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
        logger.error(msg)
    return result, msg


def delete_product(paths):
    """ removes specified product from pool
    """

    typename = paths[-2]
    indexstr = paths[-1]
    poolname = '/'.join(paths[0: -2])
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    urn = makeUrn(poolname=poolname, typename=typename, index=indexstr)
    # resourcetype = fullname(data)

    if not PM.isLoaded(poolname):
        result = '"FAILED"'
        msg = 'Pool not found: ' + poolname
        logger.error(msg)
        return result, msg
    logger.debug('DELETE product urn: ' + urn)
    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.remove(urn)
        msg = 'remove product ' + urn + ' OK.'
    except Exception as e:
        result = '"FAILED"'
        msg = 'Unable to remove product: ' + urn + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
        logger.error(msg)
    return result, msg


def register_pool(paths):
    """ Register this pool to PoolManager.
    """
    poolname = '/'.join(paths)
    fullpoolpath = os.path.join(poolpath, poolname)
    poolurl = schm + '://' + fullpoolpath
    po = PM.getPool(poolname=poolname, poolurl=poolurl)
    return '"'+po._poolurl+'"', 'register pool ' + poolname + ' OK.'


def unregister_pool(paths):
    """ Unregister this pool from PoolManager.

    Checking if the pool exists in server, and unregister or raise exception message to client.
    """

    poolname = '/'.join(paths)
    logger.debug('UNREGISTER (DELETE) POOL' + poolname)

    result = PM.remove(poolname)
    if result == 1:
        result = '"INFO"'
        msg = 'Pool not registered: ' + poolname
        return result, msg
    elif result == 0:
        msg = 'Unregister pool ' + poolname + ' OK.'
        return result, msg
    else:
        result = '"FAILED"'
        msg = 'Unable to unregister pool: ' + poolname + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
    checkpath.cache_clear()
    return result, msg


def save_product(data, paths, tag=None, serialize_in=True, serialize_out=False):
    """Save products and returns URNs.

    Saving Products to HTTPpool will have data stored on the server side. The server only returns URN strings as a response. ProductRefs will be generated by the associated httpclient pool which is the front-end on the user side.


    Returns a URN object or a list of URN objects.
    """

    typename = paths[-2]
    index = str(paths[-1])
    poolname = '/'.join(paths[0: -2])
    fullpoolpath = os.path.join(poolpath, poolname)
    poolurl = schm + '://' + fullpoolpath
    # resourcetype = fullname(data)

    if checkpath(fullpoolpath, pc['serveruser']) is None:
        result = '"FAILED"'
        msg = 'Pool directory error: ' + fullpoolpath
        return result, msg

    logger.debug('SAVE product to: ' + poolurl)
    # logger.debug(str(id(PM._GlobalPoolList)) + ' ' + str(PM._GlobalPoolList))

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.saveProduct(
            product=data, tag=tag, geturnobjs=True, serialize_in=serialize_in, serialize_out=serialize_out)
        msg = 'Save data to ' + poolurl + ' OK.'
    except Exception as e:
        result = '"FAILED"'
        msg = 'Exception : ' + str(e) + ' ' + trbk(e)
    return result, msg


def getProduct_Or_Component(paths, serialize_out=False):
    """
    """

    # paths[1] is A URN or a product type.
    for i in [1, 2]:
        if i < len(paths) and paths[i].lower().startswith('urn+'):
            # load it
            p = paths[i].split('+')
            # example ['urn', 'test', 'fdi.dataset.product.Product', '0']
            paths[i] = p[2]
            paths.insert(i+1, p[3])
            break
    lp = len(paths)
    # now paths = poolname, prod_type , ...

    mInfo = 0
    if lp == 2:
        # ex: test/fdi.dataset.Product
        # return classes[class]
        pp = paths[1]
        mp = pp.rsplit('.', 1)
        modname, ptype = mp[0], mp[1]
        cls = Classes.mapping[ptype]
        mod = importlib.import_module(modname)  # TODO
        mInfo = getattr(mod, 'ProductInfo')
        return serialize(mInfo, indent=4), 'Getting API info for %s OK' % paths[1]
    elif lp >= 3:
        return compo_cmds(paths, mInfo, serialize_out=serialize_out)

    else:
        return '"FAILED"', 'Unknown path %s' % str(paths)


def compo_cmds(paths, mInfo, serialize_out=False):

    p1 = paths[1]
    p2 = paths[2]

    if p1 == 'string':
        if p2.isnumeric() or ',' in p2:
            tsargs = p2.split(',')
            tsargs[0] = int(tsargs[0])
            pos = 3
        else:
            level = 0
            pos = 2
            tsargs = []

        compo, path_str, prod = load_compo_at(pos, paths, mInfo)
        if compo:
            result = compo.toString(*tsargs)
            msg = 'Getting toString(%s) OK' % (str(tsargs))
            resp = make_response(result)
            if 'html' in p2:
                ct = 'text/html'
            elif 'fancy_grid' in p2:
                ct = 'text/plain;charset=utf-8'
            else:
                ct = 'text/plain'
            resp.headers['Content-Type'] = ct
            return resp, msg

        else:
            return '"FAILED"', '%s: %s' % (p1, path_str)
    elif p1 == 'ls':
        pos = 2
        compo, path_str, prod = load_compo_at(pos, paths, mInfo)
        if compo:
            ls = [m for m in dir(compo) if not m.startswith('_')]
            return serialize(ls), 'Getting %s members OK' % (p1 + ':' + paths[2] + '/' + path_str)
        else:
            return '"FAILED"', '%s: %s' % (p1, path_str)
    else:
        if paths[2].isnumeric():
            # no cmd, ex: test/fdi.dataset.Product/4/...
            # send json
            pos = 1
            if len(paths) == 3 or paths[3] == '':
                # only sn number. load it
                return load_product(pos, paths, serialize_out=serialize_out)
            else:
                compo, path_str, prod = load_compo_at(pos, paths, mInfo)
                if compo:
                    return serialize(compo), 'Getting %s OK' % (p1 + ':' + paths[2] + '/' + path_str)
                else:
                    return '"FAILED"', '%s%s' % ('/'.join(paths[:3]), path_str)
        else:
            return '"FAILED"', 'Need index number %s' % str(paths)


def load_compo_at(pos, paths, mInfo):
    """ paths[pos] is cls; paths[pos+2] is 'description','meta' ..."""
    #component = fetch(paths[pos+2:], mInfo)
    # if component:
    prod, msg = load_product(pos, paths, serialize_out=False)
    if prod == '"FAILED"':
        return None, '%s. Unable to load %s.' % (msg, str(paths)), None
    compo, path_str = fetch(paths[pos+2:], prod)
    return compo, path_str, prod


def load_product(p, paths, serialize_out=False):
    """Load product paths[p]:paths[p+1] from paths[0]
    """

    typename = paths[p]
    indexstr = paths[p+1]
    poolname = paths[0]
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    urn = makeUrn(poolname=poolname, typename=typename, index=indexstr)
    # resourcetype = fullname(data)

    if not PM.isLoaded(poolname):
        result = '"FAILED"'
        msg = 'Pool not found: ' + poolname
        return result, msg

    logger.debug('LOAD product: ' + urn)
    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.loadProduct(urn=urn, serialize_out=serialize_out)
        msg = ''
    except Exception as e:
        result = '"FAILED"'
        msg = 'Exception : ' + str(e) + ' ' + trbk(e)
    return result, msg


def load_HKdata(paths):
    """Load HKdata of a pool
    """

    hkname = paths[-1]
    poolname = '/'.join(paths[0: -1])
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    # resourcetype = fullname(data)

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.readHK(serialize_out=True)
        msg = ''
    except Exception as e:
        result = '"FAILED"'
        msg = 'Exception : ' + str(e) + ' ' + trbk(e)
        raise e
    return result, msg


def load_single_HKdata(paths):
    """ Returns pool housekeeping data of the specified type: classes or urns or tags.
    """

    hkname = paths[-1]
    # paths[-2] is 'hk'
    poolname = '/'.join(paths[: -2])
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    # resourcetype = fullname(data)

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.readHK(hkname, serialize_out=True)
        msg = ''
    except Exception as e:
        result = '"FAILED"'
        msg = 'Exception : ' + str(e) + ' ' + trbk(e)
    return result, msg


# API specification for this module
APIs = {
    'GET': {'func': 'get_pool_sn',
            'cmds': {'sn': ('Return the total count for the given product type and pool_id.', {
                'prod_type': 'clsssname',
                'pool_id': 'pool name'
            })},
            },
    'PUT': {'func': 'httppool',
            'cmds': {'pool': 'url'
                     }
            },
    'POST': {'func': 'httppool',
             'cmds': {'pool': 'url'
                      }
             },
    'DELETE': {'func': 'httppool',
               'cmds': {'pool': 'url'
                        }
               }


}

# @ app.route(pc['baseurl'] + '/', methods=['GET'])
# @ app.route(pc['baseurl'] + '/api', methods=['GET'])
# def get_apis():
#     """ Makes a page for APIs described in module variable APIs. """

#     logger.debug('APIs %s' % (APIs.keys()))
#     ts = time.time()
#     l = [(a, makepublicAPI(o)) for a, o in APIs.items()]
#     w = {'APIs': dict(l), 'timestamp': ts}
#     logger.debug('ret %s' % (str(w)[:100] + ' ...'))
#     return jsonify(w)


logger.debug('END OF '+__file__)
