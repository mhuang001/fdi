# -*- coding: utf-8 -*-

from .getswag import swag
from .httppool_server import resp, excp, checkpath, unauthorized
from ..model.user import auth
from ...dataset.deserialize import deserialize_args
from ...pal.poolmanager import PoolManager as PM, DEFAULT_MEM_POOL
from ...pal.webapi import WebAPI

from flask import Blueprint, jsonify, request, current_app
from flasgger import swag_from

import shutil
import time
import copy
import json
import os
from itertools import chain
from http import HTTPStatus


endp = swag['paths']

pools_api = Blueprint('pools', __name__)

######################################
#### /  get_registered_pools   ####
######################################


@ pools_api.route('/', methods=['GET'])
# @ swag_from(endp['/']['get'])
def get_registered_pools():
    """ Returns a list of Pool IDs (pool names) of all pools registered with the Global PoolManager.
    ---
    """
    ts = time.time()
    path = current_app.config['POOLPATH_BASE']
    current_app.logger.debug('Listing all registered pools.')

    result = [p.getPoolurl() for p in PM.getMap().values()]
    msg = 'There is/are %d pools registered to the PoolManager.' % len(result)
    code = 200
    return resp(code, result, msg, ts)


######################################
#### /pools  get_pools/  reg/unreg ####
######################################


# @ pools_api.route('', methods=['GET'])
@ pools_api.route('/pools/', methods=['GET'])
# #@ swag_from(endp['/pools']['get'])
def get_pools():
    logger = current_app.logger
    if request.method in ['POST', 'PUT', 'DELETE'] and auth.current_user() == current_app.config['PC']['node']['ro_username']:
        msg = 'User %s us Read-Only, not allowed to %s.' % \
            (auth.current_user(), request.method)
        logger.debug(msg)
        return unauthorized(msg)

    ts = time.time()
    path = current_app.config['POOLPATH_BASE']
    logger.debug('Listing all directories from ' + path)

    result = get_name_all_pools(path)
    msg = '%d pools found.' % len(result)
    code = 200
    return resp(code, result, msg, ts)


def get_name_all_pools(path):
    """ Returns names of all pools in the given directory.

    """

    alldirs = []
    allfilelist = os.listdir(path)
    for file in allfilelist:
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            alldirs.append(file)
    current_app.logger.debug(path + ' has ' + str(alldirs))
    return alldirs

######################################
#### /pools/register_all pools/register_all/  ####
######################################


@ pools_api.route('/pools/register_all', methods=['PUT'])
# #@ swag_from(endp['/pools/register_all']['put'])
def register_all():
    """ Register (Load) all pools on tme server.


    """
    ts = time.time()
    pmap, bad = load_pools()
    code = 400 if len(bad) else 200
    result = ', '.join(pmap.keys())
    msg = '%d pools successfully loaded. Troubled: %s' % (len(pmap), str(bad))
    return resp(code, result, msg, ts)


def load_pools(poolnames=None):
    """
    Adding all pool to server pool storage.

    poolnames: if given as a list of poolnames, only the exisiting ones of the list will be loaded.
    Returns: a `dict` of successfully loaded pools names-pool in `good`, and troubled ones in `bad` with associated exception info.
    """

    logger = current_app.logger
    path = current_app.config['POOLPATH_BASE']
    pmap = {}
    bad = {}
    logger.debug('loading all from ' + path)
    alldirs = poolnames if poolnames else get_name_all_pools(path)
    for nm in alldirs:
        # must save the link or PM._GLOBALPOOLLIST will remove as dead weakref
        code, thepool, msg = register_pool(nm)
        if code == 200:
            pmap[nm] = thepool
        else:
            bad[nm] = nm+': '+msg

    logger.debug("Registered pools: %s in %s" % (str(list(pmap.keys())), path))
    return pmap, bad

######################################
#### /pools/unregister_all  pools/unregister_all/  ####
######################################


@ pools_api.route('/pools/unregister_all', methods=['PUT'])
# @ swag_from(endp['/pools/unregister_all']['delete'])
def unregister_all():

    ts = time.time()
    good, bad = unregister_pools()
    code = 200 if not bad else 416
    result = good
    msg = '%d pools unregistered%s' % (len(good),
                                       (' except %s.' % str(bad) if len(bad) else '.'))
    return resp(code, result, msg, ts)


def unregister_pools(poolnames=None):
    """
    Removing all pools from the PoolManager.
`w
    poolnames: if given as a list of poolnames, only the ones in the list will be unregistered.

    Returns: a list of successfully unregistered pools names in `good`, and troubled ones in `bad` with associated exception info.
    """
    logger = current_app.logger

    good = []
    notgood = []
    all_pools = poolnames if poolnames else copy.copy(list(PM.getMap().keys()))
    logger.debug('unregister pools ' + str(all_pools))

    for nm in all_pools:
        code, res, msg = unregister_pool(nm)
        if res == 'FAILED':
            notgood.append(nm+': '+msg)
        else:
            good.append(nm)
    return good, notgood

######################################
#### /pools/wipe_all  pools/wipe_all/  ####
######################################


@ pools_api.route('/pools/wipe_all', methods=['DELETE'])
@ auth.login_required
def wipe_all():
    """ Remove contents of all pools.

    Only registerable pools will be wiped. Pool directories are not removed.
    """
    ts = time.time()
    good, bad = wipe_pools()
    code = 200 if not bad else 416
    result = good
    msg = '%d pools wiped%s' % (len(good),
                                (' except %s.' % str(bad) if len(bad) else '.'))
    return resp(code, result, msg, ts)


def wipe_pools(poolnames=None):
    """
    Deleting all pools using pool api so locking is properly used.

    poolnames: if given as a list of poolnames, only the  ones in the list will be deleted.

    Returns: a list of successfully removed pools names in `good`, and troubled ones in `bad` with associated exception info.
    """
    logger = current_app.logger
    path = current_app.config['POOLPATH_BASE']
    logger.debug('DELETING pools contents from ' + path)

    # alldirs = poolnames if poolnames else get_name_all_pools(path)

    good = []
    notgood = []
    all_pools, not_loadable = load_pools(poolnames)
    names = list(all_pools.keys())
    for nm in copy.copy(names):
        thepool = all_pools[nm]
        try:
            thepool.removeAll()
            shutil.rmtree(os.path.join(path, nm))
            res = PM.remove(nm)
            if res > 1:
                notgood.append(nm+': '+str(res))
                logger.info('Pool %s not deleted.' % nm)
            else:
                good.append(nm)
                logger.info('Pool %s deleted.' % nm)
        except Exception as e:
            notgood.append(nm+': '+str(e))
    return good, notgood

######################################
#### /{pool}  get_pool/  GET  ####
######################################


@ pools_api.route('/<string:pool>', methods=['GET'])
# @ swag_from(endp['/{pool}']['get'])
def get_pool(pool):
    """ Get information of the given pool.

    Returns the state of the pool of given Pool IDs.
    """

    logger = current_app.logger

    ts = time.time()
    logger.debug('Get pool info of ' + pool)

    _, result, _ = get_pool_info(pool)
    return result


def get_pool_info(poolname, serialize_out=True):
    ''' returns information of the pool.
    '''
    msg = ''
    ts = time.time()
    FAILED = '"FAILED"' if serialize_out else 'FAILED'

    allpools = get_name_all_pools(current_app.config['POOLPATH_BASE'])
    if poolname in allpools:
        code, result, mes = load_single_HKdata(
            [poolname, 'hk', 'classes'],
            serialize_out=serialize_out)
        msg = 'Getting pool %s info.. %s.' % (poolname, mes)
    else:
        code, result, msg = 404, FAILED, poolname +\
            ' is not an exisiting Pool ID.'
    return 0, resp(code, result, msg, ts, serialize_out), 0

######################################
####  {pooolid}/register PUT /unreg DELETE  ####
######################################


@ pools_api.route('/<string:pool>', methods=['PUT'])
# @ swag_from(endp['/{pool}']['put'])
def register(pool):
    """ Register the given pool.

    Register the pool of given Pool IDs to the global PoolManager.

    :return: response made from http code, poolurl, message
    """

    logger = current_app.logger
    if auth.current_user() == current_app.config['PC']['node']['ro_username']:
        msg = 'User %s us Read-Only, not allowed to %s.' % \
            (auth.current_user(), request.method)
        logger.debug(msg)
        return unauthorized(msg)

    ts = time.time()
    logger.debug('register pool ' + pool)

    code, thepool, msg = register_pool(pool)

    return resp(code, thepool._poolurl, msg, ts)


def register_pool(pool):
    """ Register this pool to PoolManager.

    :returns: code, pool object if successful, message
    """
    poolname = pool
    fullpoolpath = os.path.join(current_app.config['POOLPATH_BASE'], poolname)
    poolurl = current_app.config['POOLURL_BASE'] + poolname
    try:
        po = PM.getPool(poolname=poolname, poolurl=poolurl)
        return 200, po, 'register pool ' + poolname + ' OK.'
    except Exception as e:
        code, result, msg = excp(
            e,
            msg='Unable to register pool: ' + poolname)
        current_app.logger.error(msg)
        return code, result, msg


@ pools_api.route('/<string:pool>', methods=['DELETE'])
# @ swag_from(endp['/{pool}']['delete'])
def unregister(pool):
    """ Unregister this pool from PoolManager.

        Check if the pool exists in server, and unregister or raise exception message to client.

    """
    logger = current_app.logger
    if auth.current_user() == current_app.config['PC']['node']['ro_username']:
        msg = 'User %s us Read-Only, not allowed to %s.' % \
            (auth.current_user(), request.method)
        logger.debug(msg)
        return unauthorized(msg)

    ts = time.time()
    logger.debug('Unregister pool ' + pool)

    code, result, msg = unregister_pool(pool)
    return resp(code, result, msg, ts)


def unregister_pool(pool):
    """ Unregister this pool from PoolManager.

    Check if the pool exists in server, and unregister or raise exception message.
    :return: http code, return value, message.
    """

    poolname = pool
    current_app.logger.debug('UNREGISTER (DELETE) POOL' + poolname)
    try:
        result = PM.remove(poolname)
        if result == 1:
            result = '1'
            msg = 'Pool not registered or referenced: ' + poolname
            code = 200
        elif result == 0:
            result = '0'
            msg = 'Unregister pool ' + poolname + ' OK.'
            code = 200
        else:
            result = 'FAILED'
            msg = 'Unable to unregister pool: ' + poolname
            code = 409
        #current_app.logger.debug(f'{code}; {result}; {msg}')
    except Exception as e:
        code, result, msg = excp(
            e,
            msg='Unable to unregister pool: ' + poolname)
        current_app.logger.error(msg)
    checkpath.cache_clear()
    return code, result, msg


######################################
####  {pool}/hk/          ####
######################################


@ pools_api.route('/<string:pool>/hk/', methods=['GET'])
# @ swag_from(endp['/{pool}']['put'])
def hk(pool):
    """ All kinds of pool housekeeping data.

    """

    logger = current_app.logger

    ts = time.time()
    pool = pool.strip('/')
    logger.debug('get HK for ' + pool)

    code, result, msg = load_HKdata([pool, 'hk'])

    return resp(code, result, msg, ts, serialize_out=True)


def load_HKdata(paths, serialize_out=True):
    """Load HKdata of a pool
    """

    hkname = paths[-1]
    poolname = '/'.join(paths[0: -1])
    poolurl = current_app.config['POOLURL_BASE'] + poolname
    # resourcetype = fullname(data)

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.readHK(serialize_out=serialize_out)
        msg = ''
        code = 200
    except Exception as e:
        code, result, msg = excp(e, serialize_out=serialize_out)
        raise e
    return code, result, msg


######################################
####  {pool}/api/               ####
######################################


@ pools_api.route('/<string:pool>/api/', methods=['GET'])
# @ swag_from(endp['/{pool}']['put'])
def api_info(pool):
    """ A list of names of allowed API methods.

    Returns a list of name of methods allowed to be called with web APIs on this pool.
    """

    logger = current_app.logger

    ts = time.time()
    logger.debug(f'get allowed API methods for {pool}')

    return resp(200, WebAPI, 'OK.', ts, serialize_out=False)


######################################
#### /{pool}/wipe  PUT/  ####
######################################


@ pools_api.route('/<string:pool>/wipe', methods=['PUT'])
@ auth.login_required
def wipe(pool):
    """ Removes all contents of the pool.

    requests all data in the pool be removed.
    """
    ts = time.time()
    logger = current_app.logger
    logger.debug(f'wipe ' + pool)

    good, bad = wipe_pools([pool])
    if bad:
        code = 416
        result = 'FAILED'
        msg = 'Unable to wipe ' + pool + ' %s %s' % (str(good), str(bad))
    else:
        code = 200
        result = 0
        msg = 'Wiping %s done.' % pool

    return resp(code, result, msg, ts)

######################################
####  {pool}/hk/{kind}          ####
######################################


@ pools_api.route('/<string:pool>/hk/<string:kind>', methods=['GET'])
# @ swag_from(endp['/{pool}']['put'])
def hk_single(pool, kind):
    """ Returns the given kind of pool housekeeping data.
    """

    logger = current_app.logger

    ts = time.time()
    pool = pool.strip('/')
    logger.debug(f'get {kind} HK for ' + pool)

    code, result, msg = load_single_HKdata([pool, 'hk', kind])

    return resp(code, result, msg, ts, serialize_out=True)


def load_single_HKdata(paths, serialize_out=True):
    """ Returns pool housekeeping data of the specified type: classes or urns or tags.
    """

    hkname = paths[-1]
    # paths[-2] is 'hk'
    poolname = '/'.join(paths[: -2])
    poolurl = current_app.config['POOLURL_BASE'] + poolname
    # resourcetype = fullname(data)

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.readHK(hkname, serialize_out=serialize_out)
        code, msg = 200, hkname + ' HK data returned OK'
    except Exception as e:
        code, result, msg = excp(e, serialize_out=serialize_out)
    return code, result, msg

######################################
####  {pool}/count/{kind}          ####
######################################


@ pools_api.route('/<string:pool>/count/<string:data_type>', methods=['GET'])
# @ swag_from(endp['/{pool}']['put'])
def count(pool, data_type):
    """ Returns the number of given type of data in the given pool.

    :data_type:  (part of) dot-separated full class name of data items in pool.
    """

    logger = current_app.logger

    ts = time.time()
    pool = pool.strip('/')
    logger.debug(f'get {data_type} count for ' + pool)

    code, result, msg = get_prod_count(data_type, pool)

    return resp(code, result, msg, ts, serialize_out=False)


def get_prod_count(prod_type, pool_id):
    """ Return the total count for the given product type and pool_id in the directory.

    'prod_type': (part of) 'clsssname',
    'pool_id': 'pool name'

    """

    logger = current_app.logger
    logger.debug('### method %s prod_type %s pool %s***' %
                 (request.method, prod_type, pool_id))
    res = 0
    nm = []

    path = os.path.join(current_app.config['POOLPATH_BASE'], pool_id)
    if os.path.exists(path):
        for i in os.listdir(path):
            if i[-1].isnumeric() and prod_type in i:
                res = res+1
                nm.append(i)
    else:
        return 400, 'FAILED', f'Pool {pool} not found.'
    s = str(nm)
    logger.debug(prod_type + ' found '+s)
    return 200, res, 'Counting %d %s files OK.' % (res, prod_type)


######################################
####  {pool}/api/{method}/{args} ####
######################################


@ pools_api.route('/<string:pool>/api/<string:method_args>', methods=['GET'])
@ pools_api.route('/<string:pool>/api/<string:method_args>/', methods=['GET'])
@ auth.login_required
def api(pool, method_args):
    """ Call api mathods on the running pool and returns the result.

    """

    logger = current_app.logger

    ts = time.time()
    logger.debug(f'get API {method_args} for {pool}')

    paths = [pool, 'api', method_args]
    lp0 = len(paths)

    code, result, msg = call_pool_Api(paths, serialize_out=False)

    return resp(code, result, msg, ts, serialize_out=False)


def call_pool_Api(paths, serialize_out=False):
    """ Call api mathods on the running pool and returns the result.

    return: value if args is pool property; execution result if method. 
    """

    FAILED = '"FAILED"' if serialize_out else 'FAILED'
    logger = current_app.logger
    ts = time.time()

    args, kwds = [], {}

    # the unquoted args. may have ',' in strings
    #quoted_m_args = paths[ind_meth+1]

    # from the unquoted url extract the fist path segment.
    quoted_m_args = request.url.split(
        paths[0] + '/' + paths[1] + '/')[1].strip('/')
    logger.debug(f'get API {quoted_m_args}')
    # get command positional arguments and keyword arguments
    code, m_args, kwds = deserialize_args(
        quoted_m_args, serialize_out=serialize_out)
    if code != 200:
        result, msg = m_args, kwds
        return 0, resp(422, result, msg, ts, serialize_out=False), 0

    method = m_args[0]
    # if 'getPoolurl' in method:
    #    __import__('pdb').set_trace()
    if method not in WebAPI:
        return 0, resp(400, FAILED,
                       'Unknown web API method: %s.' % method,
                       ts, serialize_out=False), 0
    args = m_args[1:] if len(m_args) > 1 else []
    kwdsexpr = [str(k)+'='+str(v) for k, v in kwds.items()]
    msg = '%s(%s)' % (method, ', '.join(
        chain(map(str, args), kwdsexpr)))
    logger.debug('WebAPI ' + msg)

    poolname = paths[0]
    poolurl = current_app.config['POOLURL_BASE'] + poolname
    if not PM.isLoaded(poolname):
        result = FAILED
        msg = 'Pool not found or not registered: ' + poolname
        logger.error(msg)
        return 0, resp(404, result, msg, ts, serialize_out=False), 0

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        res = getattr(poolobj, method)(*args, **kwds)
        result = res
        msg = msg + ' OK.'
        code = 200
    except Exception as e:
        code, result, msg = excp(e, 422, serialize_out=serialize_out)
        logger.error(msg)

    return 0, resp(code, result, msg, ts, serialize_out=False), 0