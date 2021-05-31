# -*- coding: utf-8 -*-

#from . import server_skeleton
#from .server_skeleton import init_conf_clas, User, checkpath, app, auth, pc
from ..utils.common import lls
from ..dataset.deserialize import deserialize
from ..dataset.serializable import serialize
from ..pal.poolmanager import PoolManager
from ..pal.query import MetaQuery, AbstractQuery
from ..pal.urn import makeUrn, parseUrn
from ..pal.webapi import WebAPI
from ..dataset.product import Product
from ..dataset.classes import Classes
from ..utils import getconfig
from ..utils.common import fullname, trbk, getUidGid
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
import functools
import datetime
import operator
from collections import ChainMap
from itertools import chain
import importlib
from flask import Flask, request, make_response, jsonify
from flask.wrappers import Response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
    strset = str
    from urllib.parse import urlparse
else:
    PY3 = False
    # strset = (str, unicode)
    strset = str
    from urlparse import urlparse


######################################
#### Application Factory Function ####
######################################


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    config_object = config_object if config_object else getconfig.getConfig()
    app.config['PC'] = config_object
    import logging
    import logging.config
    from .logdict import logdict
    logging.config.dictConfig(logdict)
    # '/var/log/pns-server.log'
    # logdict['handlers']['file']['filename'] = '/tmp/server.log'
    app.logger = logging.getLogger(__name__)
    # initialize_extensions(app)
    # register_blueprints(app)
    init_httppool_server(app)
    return app


def init_conf_clas(pc, app):

    from ..dataset.classes import Classes

    # setup user class mapping
    clp = pc['userclasses']
    app.logger.debug('User class file '+clp)
    if clp == '':
        Classes.updateMapping()
    else:
        clpp, clpf = os.path.split(clp)
        sys.path.insert(0, os.path.abspath(clpp))
        # print(sys.path)
        pcs = __import__(clpf.rsplit('.py', 1)[
            0], globals(), locals(), ['PC'], 0)
        pcs.PC.updateMapping()
        Classes.updateMapping(pcs.PC.mapping)
        app.logger.debug('User classes: %d found.' % len(pcs.PC.mapping))
    return Classes


class User():

    def __init__(self, name, passwd, role='read_only'):

        self.username = name
        self.password = passwd
        self.registered_on = datetime.datetime.now()
        self.hashed_password = generate_password_hash(passwd)
        self.role = role
        self.authenticated = False

    def is_correct_password(self, plaintext_password):

        return check_password_hash(plaintext_password, self.hashed_password)

    def __repr__(self):
        return f'<User: {self.username}>'


uspa = operator.attrgetter('username', 'password')


@functools.lru_cache(6)
def checkpath(path, un):
    """ Checks  the directories and creats if missing.

    path: str. can be resolved with Path.
    un: server user name
    """
    app.logger.debug('path %s user %s' % (path, un))

    p = Path(path).resolve()
    if p.exists():
        if not p.is_dir():
            msg = str(p) + ' is not a directory.'
            app.logger.error(msg)
            return None
        else:
            # if path exists and can be set owner and group
            if p.owner() != un or p.group() != un:
                msg = str(p) + ' owner %s group %s. Should be %s.' % \
                    (p.owner(), p.group(), un)
                app.logger.warning(msg)
    else:
        # path does not exist

        msg = str(p) + ' does not exist. Creating...'
        app.logger.debug(msg)
        p.mkdir(mode=0o775, parents=True, exist_ok=True)
        app.logger.info(str(p) + ' directory has been made.')

    #app.logger.info('Setting owner, group, and mode...')
    if not setOwnerMode(p, un):
        return None

    app.logger.debug('checked path at ' + str(p))
    return p


def init_httppool_server(app):
    """ Init a global HTTP POOL """

    # local.py config
    pc = app.config['PC']
    # class namespace
    Classes = init_conf_clas(pc, app)
    lookup = ChainMap(Classes.mapping, globals(), vars(builtins))
    app.config['LOOKUP'] = lookup

    # auth
    auth = HTTPBasicAuth()
    app.config['AUTH'] = auth

    # users
    # effective group of current process
    uid, gid = getUidGid(pc['serveruser'])
    app.logger.info("Serveruser %s's uid %d and gid %d..." %
                    (pc['serveruser'], uid, gid))
    # os.setuid(uid)
    # os.setgid(gid)
    xusers = {
        "rw": generate_password_hash(pc['node']['username']),
        "ro": generate_password_hash(pc['node']['password'])
    }
    users = [
        User(pc['node']['username'], pc['node']['password'], 'read_write'),
        User(pc['node']['ro_username'], pc['node']
             ['ro_password'], 'read_only')
    ]
    app.config['USERS'] = users

    # PoolManager is a singleton
    from ..pal.poolmanager import PoolManager as PM, DEFAULT_MEM_POOL
    if PM.isLoaded(DEFAULT_MEM_POOL):
        app.logger.debug('cleanup DEFAULT_MEM_POOL')
        PM.getPool(DEFAULT_MEM_POOL).removeAll()
    app.logger.debug('Done cleanup PoolManager.')
    app.logger.debug('ProcID %d 1st reg %s' % (os.getpid(),
                                               str(app._got_first_request))
                     )
    PM.removeAll()
    app.config['POOLMANAGER'] = PM

    # pool-related paths
    # the httppool that is local to the server
    scheme = 'server'
    _basepath = PM.PlacePaths[scheme]
    poolpath = os.path.join(_basepath, pc['api_version'])

    if checkpath(poolpath, pc['serveruser']) is None:
        app.logger.error('Store path %s unavailable.' % poolpath)
        sys.exit(-2)

    app.config['POOLSCHEME'] = scheme
    app.config['POOLPATH'] = poolpath


# =============HTTP POOL=========================
#auth = HTTPBasicAuth()
#app = create_app()


@app.before_first_request
def init(app):
    global pc, PM, basepath, poolpath, lookup, auth
    pc, lookup = app.config['PC'], app.config['LOOKUP']
    PM = app.config['POOLMANAGER']
    poolpath = app.config['POOLPATH']
    poolurl_base = app.config['POOLSCHEME'] + '://' + poolpath + '/'
    auth = app.config['AUTN']


def getallpools(path):
    """ Returns names of all pools in the given directory.

    """
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
    app.logger.debug('loading all from ' + path)

    alldirs = getallpools(path)
    for poolname in alldirs:
        poolurl = schm + '://' + os.path.join(poolpath, poolname)
        PM.getPool(poolname=poolname, poolurl=poolurl)
        app.logger.info("Registered pool: %s in %s" % (poolname, poolpath))


def get_prod_count(prod_type, pool_id):
    """ Return the total count for the given product type and pool_id in the directory.

    'prod_type': 'clsssname',
    'pool_id': 'pool name'

    """

    app.logger.debug('### method %s prod_type %s poolID %s***' %
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
    app.logger.debug('found '+s)
    return str(res), 'Counting %s files OK'


@ app.route(pc['baseurl'], methods=['GET', 'POST'])
@ app.route(pc['baseurl']+'/', methods=['GET', 'POST'])
@ app.route(pc['baseurl']+'/pools', methods=['GET'])
def get_pools():
    if request.method in ['POST', 'PUT', 'DELETE'] and auth.current_user() == pc['node']['ro_username']:
        msg = 'User %s us Read-Only, not allowed to %s.' % \
            (auth.current_user(), request.method)
        app.logger.debug(msg)
        return server_skeleton.unauthorized(msg)

    ts = time.time()
    path = poolpath
    app.logger.debug('Listing all directories from ' + path)

    result = serialize(getallpools(path))
    msg = 'pools found.'
    w = '{"result": %s, "msg": "%s", "timestamp": %f}' % (
        result, msg, ts)
    app.logger.debug(lls(w, 240))
    resp = make_response(w)
    resp.headers['Content-Type'] = 'application/json'
    return resp


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
        allpools = getallpools(poolpath)
        if cmd in allpools:
            cls = load_single_HKdata([cmd, 'hk', 'classes'])
            result, msg = cls, 'Getting pool %s info OK'
        else:
            result, msg = '"FAILED"', cmd + ' is not valid.'

    w = '{"result": %s, "msg": "%s", "timestamp": %f}' % (
        result, msg, ts)
    app.logger.debug(lls(w, 240))
    resp = make_response(w)
    resp.headers['Content-Type'] = 'application/json'
    return resp

# @ app.route(pc['baseurl'] + '/sn' + '/<string:prod_type>' + '/<string:pool_id>', methods=['GET'])


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
    if request.method in ['POST', 'PUT', 'DELETE'] and auth.current_user() == pc['node']['ro_username']:
        msg = 'User %s us Read-Only, not allowed to %s.' % \
            (auth.current_user(), request.method)
        app.logger.debug(msg)
        return server_skeleton.unauthorized(msg)

    username = request.authorization.username
    paths = pool.split('/')
    if 0:
        import pdb
        pdb.set_trace()

    lp0 = len(paths)
    if lp0 == 0:
        result = getinfo()

    # if paths[-1] == '':
    #    del paths[-1]

    # paths[0] is A URN
    if paths[0].lower().startswith('urn+'):
        p = paths[0].split('+')
        # example ['urn', 'test', 'fdi.dataset.product.Product', '0']
        paths = p[1:] + paths[1:] if lp0 > 1 else []

    # paths[1] is A URN
    if lp0 > 1 and paths[1].lower().startswith('urn+'):
        p = paths[1].split('+')
        # example ['urn', 'test', 'fdi.dataset.product.Product', '0']
        paths = p[1:] + paths[2:] if lp0 > 2 else []
    # paths is normalized to [poolname, ... ]
    lp = len(paths)
    ts = time.time()
    # do not deserialize if set True. save directly to disk
    serial_through = True
    app.logger.debug('*** method %s paths %s ***' % (request.method, paths))

    if request.method == 'GET':
        # TODO modify client loading pool , prefer use load_HKdata rather than load_single_HKdata, because this will generate enormal sql transaction
        if lp == 1:
            result = getinfo(path[0])
        elif lp == 2:
            p1 = paths[1]
            if p1 == 'hk':  # Load all HKdata
                result, msg = load_HKdata(paths)
                # save_action(username=username, action='READ', pool=paths[0])
            elif p1 == 'api':
                result, msg = call_pool_Api(paths)
            else:
                result, msg = getProduct_Or_Component(
                    paths, serialize_out=serial_through)
        elif lp == 3:
            p1 = paths[1]
            if p1 == 'hk' and paths[2] in ['classes', 'urns', 'tags']:
                # Retrieve single HKdata
                result, msg = load_single_HKdata(paths)
                # save_action(username=username, action='READ', pool=paths[0])
            elif p1 == 'count':  # prod count
                result, msg = get_prod_count(paths[2], paths[0])
            elif p1 == 'api':
                result, msg = call_pool_Api(paths)
            else:
                result, msg = getProduct_Or_Component(
                    paths, serialize_out=serial_through)
        elif lp > 3:
            p1 = paths[1]
            if p1 == 'api':
                result, msg = call_pool_Api(paths)
            else:
                result, msg = getProduct_Or_Component(
                    paths, serialize_out=serial_through)
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
    # app.logger.debug(pprint.pformat(w, depth=3, indent=4))
    s = w  # serialize(w)
    app.logger.debug(lls(s, 240))
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


Builtins = vars(builtins)


def mkv(v, t):
    """
    return v with a tyoe specified by t.

    t: 'NoneType' or any name in ``Builtins``.
    """

    m = v if t == 'str' else None if t == 'NoneType' else Builtins[t](
        v) if t in Builtins else deserialize(v)
    return m


def parseApiArgs(all_args):
    """ parse the command path to get positional and keywords arguments.

    all_args: a list of path segments for the args list.
    """
    lp = len(all_args)
    args, kwds = [], {}
    if lp % 2 == 1:
        # there are odd number of args+key+val
        # the first seg after ind_meth must be all the positional args
        try:
            tyargs = all_args[0].split('|')
            for a in tyargs:
                print(a)
                v, c, t = a.rpartition(':')
                args.append(mkv(v, t))
        except IndexError as e:
            result = '"FAILED"'
            msg = 'Bad arguement format ' + all_args[0] + \
                ' Exception: ' + str(e) + ' ' + trbk(e)
            app.logger.error(msg)
            return result, msg
        kwstart = 1
    else:
        kwstart = 0
    # starting from kwstart are the keyword arges k1|v1 / k2|v2 / ...

    try:
        while kwstart < lp:
            v, t = all_args[kwstart].rsplit(':', 1)
            kwds[all_args[kwstart]] = mkv(v, t)
            kwstart += 2
    except IndexError as e:
        result = '"FAILED"'
        msg = 'Bad arguement format ' + str(all_args[kwstart:]) + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
        app.logger.error(msg)
        return result, msg

    return args, kwds


def call_pool_Api(paths):
    """ run api calls on the running pool.

    """
    # index of method name
    ind_meth = 2
    # remove empty trailing strings
    for o in range(len(paths), 1, -1):
        if paths[o-1]:
            break

    paths = paths[:o]
    lp = len(paths)
    method = paths[ind_meth]
    if method not in WebAPI:
        return '"FAILED"', 'Unknown web API method: %s.' % method
    args, kwds = [], {}

    if 0:
        poolname = paths[0]
        s = PM.isLoaded(poolname)
        import pdb
        pdb.set_trace()
    all_args = paths[ind_meth+1:]
    if lp > ind_meth:
        # get command positional arguments and keyword arguments
        args, kwds = parseApiArgs(all_args)
        if args == '"FAILED"':
            result, msg = args, kwds
        else:
            kwdsexpr = [str(k)+'='+str(v) for k, v in kwds.items()]
            msg = '%s(%s)' % (method, ', '.join(
                chain(map(str, args), kwdsexpr)))
            app.logger.debug('WebAPI ' + msg)

    poolname = paths[0]
    poolurl = schm + '://' + os.path.join(poolpath, poolname)
    if not PM.isLoaded(poolname):
        result = '"FAILED"'
        msg = 'Pool not found: ' + poolname
        app.logger.error(msg)
        return result, msg

    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        res = getattr(poolobj, method)(*args, **kwds)
        result = serialize(res)
        msg = msg + ' OK.'
    except Exception as e:
        result = '"FAILED"'
        msg = 'Unable to complete ' + msg + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
        app.logger.error(msg)
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
        app.logger.error(msg)
        return result, msg
    app.logger.debug('DELETE product urn: ' + urn)
    try:
        poolobj = PM.getPool(poolname=poolname, poolurl=poolurl)
        result = poolobj.remove(urn)
        msg = 'remove product ' + urn + ' OK.'
    except Exception as e:
        result = '"FAILED"'
        msg = 'Unable to remove product: ' + urn + \
            ' Exception: ' + str(e) + ' ' + trbk(e)
        app.logger.error(msg)
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
    app.logger.debug('UNREGISTER (DELETE) POOL' + poolname)

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

    app.logger.debug('SAVE product to: ' + poolurl)
    # app.logger.debug(str(id(PM._GlobalPoolList)) + ' ' + str(PM._GlobalPoolList))

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
    """ Get the component and the associated command and return 

    """
    lp = len(paths)

    for cmd_ind in range(1, lp):
        cmd = paths[cmd_ind]
        if cmd.startswith('$'):
            cmd = cmd.lstrip('$')
            paths[cmd_ind] = cmd
            break
    else:
        cmd = ''

    # args if found command and there is something after it
    cmd_args = paths[cmd_ind+1:] if cmd and (lp - cmd_ind > 1)else ['']
    # prod type
    pt = paths[1]
    # index
    pi = paths[2]
    # path of prod or component
    compo_path = paths[1:cmd_ind] if cmd else paths[1:]

    if cmd == 'string':
        if cmd_args[0].isnumeric() or ',' in cmd_args[0]:
            # list of arguments to be passed to :meth:`toString`
            tsargs = cmd_args[0].split(',')
            tsargs[0] = int(tsargs[0]) if tsargs[0] else 0
        else:
            tsargs = []
        # get the component'

        compo, path_str, prod = load_compo_at(1, paths[:-1], mInfo)
        if compo is not None:
            result = compo.toString(*tsargs)
            msg = 'Getting toString(%s) OK' % (str(tsargs))
            resp = make_response(result)
            if 'html' in cmd_args:
                ct = 'text/html'
            elif 'fancy_grid' in cmd_args:
                ct = 'text/plain;charset=utf-8'
            else:
                ct = 'text/plain'
            resp.headers['Content-Type'] = ct
            return resp, msg

        else:
            return '"FAILED"', '%s: %s' % (cmd, path_str)
    elif cmd == '' and paths[-1] == '':
        # command is '' and url endswith a'/'
        compo, path_str, prod = load_compo_at(1, paths[:-1], mInfo)
        if compo:
            ls = [m for m in dir(compo) if not m.startswith('_')]
            return serialize(ls), 'Getting %s members OK' % (cmd + ':' + path_str)
        else:
            return '"FAILED"', '%s: %s' % (cmd, path_str)
    elif lp == 3:
        # url ends with index
        # no cmd, ex: test/fdi.dataset.Product/4
        # send json of the prod

        return load_product(1, paths, serialize_out=serialize_out)
    elif 1:
        # no cmd, ex: test/fdi.dataset.Product/4
        # send json of the prod component
        compo, path_str, prod = load_compo_at(1, paths, mInfo)
        if compo:
            return serialize(compo), 'Getting %s OK' % (cmd + ':' + paths[2] + '/' + path_str)
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

    app.logger.debug('LOAD product: ' + urn)
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


def setOwnerMode(p, username):
    """ makes UID and GID set to those of serveruser given in the config file. This function is usually done by the initPTS script.
    """

    app.logger.debug('set owner, group to %s, mode to 0o775' % username)

    uid, gid = getUidGid(username)
    if uid == -1 or gid == -1:
        return None
    try:
        chown(str(p), uid, gid)
        chmod(str(p), mode=0o775)
    except Exception as e:
        msg = 'cannot set input/output dirs owner to ' + \
            username + ' or mode. check config. ' + str(e) + trbk(e)
        app.logger.error(msg)
        return None

    return username


@auth.verify_password
def verify_password(username, password):
    app.logger.debug('verify user/pass')
    if (username, password) in uspa(users):
        return username

# import requests
# from http.client import HTTPConnection
# HTTPConnection.debuglevel = 1


# @auth.verify_password
# def verify(username, password):
#     """This function is called to check if a username /
#     password combination is valid.
#     """
#     if not (username and password):
#         return False
#     return username == pc['node']['username'] and password == pc['node']['password']
if 0:
    pass
    # elif username == pc['auth_user'] and password == pc['auth_pass']:

    # else:
    #     password = str2md5(password)
    #     try:
    #         conn = mysql.connector.connect(host = pc['mysql']['host'], port=pc['mysql']['port'], user =pc['mysql']['user'], password = pc['mysql']['password'], database = pc['mysql']['database'])
    #         if conn.is_connected():
    #             app.logger.info("connect to db successfully")
    #             cursor = conn.cursor()
    #             cursor.execute("SELECT * FROM userinfo WHERE userName = '" + username + "' AND password = '" + password + "';" )
    #             record = cursor.fetchall()
    #             if len(record) != 1:
    #                 app.logger.info("User : " + username + " auth failed")
    #                 conn.close()
    #                 return False
    #             else:
    #                 conn.close()
    #                 return True
    #         else:
    #             return False
    #     except Error as e:
    #         app.logger.error("Connect to database failed: " +str(e))


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

#     app.logger.debug('APIs %s' % (APIs.keys()))
#     ts = time.time()
#     l = [(a, makepublicAPI(o)) for a, o in APIs.items()]
#     w = {'APIs': dict(l), 'timestamp': ts}
#     app.logger.debug('ret %s' % (str(w)[:100] + ' ...'))
#     return jsonify(w)


def makepublicAPI(o):
    """ Provides API specification for command given. """
    api = []

    for cmd, cs in o['cmds'].items():
        if not issubclass(cs.__class__, tuple):  # e.g. 'run':run
            c = cs
            kwds = {}
        else:  # e.g. 'sleep': (dosleep, dict(ops='1'))
            c, kwds = cs
        desc = c.__doc__ if isinstance(c, types.FunctionType) else c
        d = {}
        d['description'] = desc
        d['URL'] = url_for(o['func'],
                           cmd=cmd,
                           **kwds,
                           _external=True)
        api.append(d)
    # print('******* ' + str(api))
    return api


@app.errorhandler(400)
def bad_request(error):
    ts = time.time()
    w = {'error': 'Bad request.', 'message': str(error), 'timestamp': ts}
    return make_response(jsonify(w), 400)


@app.errorhandler(401)
def unauthorized(error):
    ts = time.time()
    w = {'error': 'Unauthorized. Authentication needed to modify.',
         'message': str(error), 'timestamp': ts}
    return make_response(jsonify(w), 401)


@app.errorhandler(404)
def not_found(error):
    ts = time.time()
    w = {'error': 'Not found.', 'message': str(error), 'timestamp': ts}
    return make_response(jsonify(w), 404)


@app.errorhandler(409)
def conflict(error):
    ts = time.time()
    w = {'error': 'Conflict. Updating.',
         'message': str(error), 'timestamp': ts}
    return make_response(jsonify(w), 409)
