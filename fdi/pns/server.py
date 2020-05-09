# -*- coding: utf-8 -*-

from ..utils.common import trbk
from ..dataset.deserialize import deserializeClassID
from ..dataset.serializable import serializeClassID
from ..dataset.dataset import GenericDataset, ArrayDataset, TableDataset
from ..dataset.product import Product
from ..dataset.finetime import FineTime1
from ..dataset.baseproduct import History
from ..dataset.classes import Classes
from .pnsconfig import pnsconfig as pc

import datetime
import time
import sys
import pwd
import grp
import os
from os.path import isfile, isdir, join, expanduser, expandvars
from os import listdir, chown, chmod, environ, setuid, setgid
from pathlib import Path
import types
from subprocess import Popen, PIPE, TimeoutExpired, run as srun
import pkg_resources
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import filelock
import pdb

# from .logdict import logdict
# '/var/log/pns-server.log'
# logdict['handlers']['file']['filename'] = '/tmp/server.log'
import logging
# import logging.config
# create logger
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARN)
logger.setLevel(logging.DEBUG)
if sys.version_info[0] > 2:
    logging.getLogger("urllib3").setLevel(logging.WARN)
else:
    pass
logging.getLogger("filelock").setLevel(logging.INFO)
logger.debug('logging level %d' % (logger.getEffectiveLevel()))

print('pdb.set_trace()')


def getConfig():
    # default configuration is provided. Copy pnsconfig.py to ~/.config/pnslocal.py
    env = expanduser(expandvars('$HOME'))
    # apache wsgi will return '$HOME' with no expansion
    env = '/root' if env == '$HOME' else env
    confp = join(env, '.config')
    sys.path.insert(0, confp)
    try:
        from pnslocal import pnsconfig
        logger.debug('Read from configuration file in dir '+confp)
        return pnsconfig
    except ModuleNotFoundError as e:
        logger.warn(str(
            e) + '. Use default config in fdi/pns/pnsconfig.py. Copy it to ~/.config/pnslocal.py and make persistent customization there.')
        return {}


pc = getConfig()
clp = pc['userclasses']
logger.debug('User class file '+clp)
if clp == '':
    pass
else:
    clpp, clpf = os.path.split(clp)
    sys.path.insert(0, os.path.abspath(clpp))
    # print(sys.path)
    pcs = __import__(clpf.rsplit('.py', 1)[
        0], globals(), locals(), ['prjcls'], 0)
    Classes.mapping = pcs.prjcls
    logger.debug('User classes: %d found.' % len(pcs.prjcls))

# logger.debug('logging file %s' % (logdict['handlers']['file']['filename']))


app = Flask(__name__)
auth = HTTPBasicAuth()


def _execute(cmd, input=None, timeout=10):
    """ Executes a command on the server host in the pnshome directory and returns run status. Default imeout is 10sec. Run as user set byas.
    returns {return code, msg}
    """

    logger.debug('%s inp:%s tout: %d' %
                 (str(cmd), str(input), timeout))
    sta = {'command': str(cmd)}
    pnsh = pc['paths']['pnshome']
    asuser = pc['ptsuser']

    try:
        # https://stackoverflow.com/a/6037494
        pw_record = pwd.getpwnam(asuser)
        user_name = pw_record.pw_name
        user_home_dir = pw_record.pw_dir
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid
        env = environ.copy()
        env['HOME'] = user_home_dir
        env['LOGNAME'] = user_name
        env['PWD'] = pnsh
        env['USER'] = user_name

        def chusr(user_uid, user_gid):
            def result():
                setgid(user_gid)
                setuid(user_uid)
                logger.debug('set uid=%d gid=%d' % (user_uid, user_gid))
            return result
        executable = None

        # /etc/sudoer: apache ALL:(vvpp) NOPASSWD: ALL
        # gpasswd -a vvpp apache
        # cmd = ['sudo', '-u', asuser, 'bash', '-l', '-c'] + cmd
        # cmd = ['sudo', '-u', asuser] + cmd
        logger.debug('Popen %s env:%s uid: %d gid:%d' %
                     (str(cmd), str(env)[: 40] + ' ... ', user_uid, user_gid))
        proc = Popen(cmd, executable=executable,
                     stdin=PIPE, stdout=PIPE, stderr=PIPE,
                     preexec_fn=None,
                     cwd=pnsh,
                     env=env, shell=False,
                     encoding='utf-8')  # , universal_newlines=True)
    except Exception as e:
        msg = repr(e) + trbk(e) + ' ' + \
            (e.child_traceback if hasattr(e, 'child_traceback') else '')
        return {'returncode': -1, 'message': msg}

    try:
        sta['stdout'], sta['stderr'] = proc.communicate(timeout=timeout)
        sta['returncode'] = proc.returncode
    except TimeoutExpired:
        # The child process is not killed if the timeout expista,
        # so in order to cleanup properly a well-behaved application
        # should kill the child process and finish communication
        # https://docs.python.org/3.6/library/subprocess.html?highlight=subprocess#subprocess.Popen.communicate
        proc.kill()
        sta['stdout'], sta['stderr'] = proc.communicate()
        sta['returncode'] = proc.returncode

    return sta

    cp = srun(cmd, input=input, stdout=PIPE, stderr=PIPE,
              cwd=pc['paths']['pnshome'], timeout=timeout,
              encoding='utf-8', shell=True)  # universal_newlines=True)
    sta['stdout'], sta['stderr'] = cp.stdout, cp.stderr
    sta['returncode'] = cp.returncode
    return sta


def checkpath(path):
    logger.debug(path)
    p = Path(path).resolve()
    if p.exists():
        if not p.is_dir():
            msg = str(p) + ' is not a directory.'
            logger.error(msg)
            return None
    else:
        p.mkdir()
        un = pc['serveruser']
        try:
            uid = pwd.getpwnam(un).pw_uid
        except KeyError as e:
            msg = 'cannot set input/output dirs owner to ' + \
                un + '. check config. ' + str(e) + trbk(e)
            logger.error(msg)
            return None
        try:
            gid = grp.getgrnam(un).gr_gid
        except KeyError as e:
            gid = -1
            logger.warn('input/output group unchanged. ' + str(e) + trbk(e))
        try:
            chown(str(p), uid, gid)
            chmod(str(p), mode=0o775)
        except Exception as e:
            msg = 'cannot set input/output dirs owner to ' + \
                un + ' or mode. check config. ' + str(e) + trbk(e)
            logger.error(msg)
            return None

        logger.info(str(p) + ' directory has been made.')
    logger.debug('checked path at ' + str(p))
    return p


def initPTS(d=None):
    """ Initialize the Processing Task Software by running the init script defined in the config. Execution on the server host is in the pnshome directory and run result and status are returned. If input/output directories cannot be created with serveruser as owner, Error401 will be given.
    """

    logger.debug(str(d))

    pnsh = pc['paths']['pnshome']
    p = checkpath(pnsh)
    if p is None:
        abort(401)

    pi = checkpath(pc['paths']['inputdir'])
    po = checkpath(pc['paths']['outputdir'])
    if pi is None or po is None:
        abort(401)

    indata = deserializeClassID(d)

    if hasattr(indata, '__iter__') and 'timeout' in indata:
        timeout = indata['timeout']
    else:
        timeout = pc['timeout']

    stat = _execute(pc['scripts']['init'], timeout=timeout)
    return stat['returncode'], stat


def testinit(d=None):
    """     Renames the 'init' 'config' 'run' 'clean' scripts to '.save' and points it to the '.ori' scripts.
    """

    pnsh = pc['paths']['pnshome']
    p = checkpath(pnsh)
    if p is None:
        abort(401)

    pi = checkpath(pc['paths']['inputdir'])
    po = checkpath(pc['paths']['outputdir'])
    if pi is None or po is None:
        abort(401)

    # hf = pkg_resources.resource_filename("pns.resources", "runPTS")
    timeout = pc['timeout']
    scpts = [x[0] for x in pc['scripts'].values()]
    logger.debug('mv -f and ln -s :' + str())
    for ni in scpts:
        try:
            p = Path(ni)
            if not p.is_symlink:
                p.rename(ni + '.save')
            if not p.samefile(ni + '.ori'):
                p.unlink()
                p.symlink_to(ni + '.ori')
        except Exception as e:
            msg = 'rename or ln failed ' + str(e) + trbk(e)
            return -1,  msg
    return 0, ''


def configPNS(d=None):
    """ Configure the PNS itself by replacing the pnsconfig var
    """
    global pc
    logger.debug(str(d)[: 80] + '...')
    # logger.debug('before configering pns ' + str(pc))
    try:
        indata = deserializeClassID(d)
        pc = indata['input']
    except Exception as e:
        re = -1
        msg = str(e)
    else:
        re = pc
        msg = ''
    # logger.debug('after configering pns ' + str(pc))

    return re, msg


def configPTS(d=None):
    """ Configure the Processing Task Software by running the config script. Ref init PTS.
    """

    logger.debug(str(d))
    indata = deserializeClassID(d)

    if hasattr(indata, '__iter__') and 'timeout' in indata:
        timeout = indata['timeout']
    else:
        timeout = pc['timeout']

    stat = _execute(pc['scripts']['config'], timeout=timeout)
    return stat['returncode'], stat


def uploadScript(op, d=None):
    """
    """

    return -1, 'not implemented'


def cleanPTS(d):
    """ Removing traces of past runnings the Processing Task Software.
    """
    # timeout is imported and needs to be declared global if referenced in ifs

    logger.debug(str(d))
    indata = deserializeClassID(d)

    if hasattr(indata, '__iter__') and 'timeout' in indata:
        timeout = indata['timeout']
    else:
        timeout = pc['timeout']

    stat = _execute(pc['scripts']['clean'], timeout=timeout)
    return stat['returncode'], stat


def defaultprocessinput(data):
    """
    puts all undecoded json to every files.
    """

    pi = Path(pc['paths']['inputdir'])

    for f in data:
        fp = pi.joinpath(f)
        if fp.exists():
            logger.debug('infile mode 0%o ' % (fp.stat().st_mode))
            fp.rename(str(fp) + '.old')
        with fp.open(mode=data[f]['mode']) as inf:
            inf.write(data[f]['contents'])
    logger.debug(str(list(data.keys())) + ' written.')


def defaultprocessoutput(filemode):
    """
    reads each of the files and returns the contents in a filename indexed dict.
    """
    res = {}
    po = Path(pc['paths']['outputdir'])
    for fn in filemode:
        with po.joinpath(fn).open(mode=filemode[fn]) as outf:
            res[fn] = outf.read()
    logger.debug(str(list(res.keys())) + ' read.')
    return res


def testrun(d):
    """
    """
    logger.debug('for hello')

    def processinput(d, indata):
        """ put json decoded input.theName to file 'infile'
        """
        contents = indata['input']['theName'].data
        defaultprocessinput({'infile': {'contents': contents, 'mode': 'w+'}})

    def processoutput(d, indata):
        """ Read every file in pc.paths.output and put their contents in a dict. process the result to required form -- a product
        """
        res = defaultprocessoutput({'outfile': 'r'})

        runner, cause = indata['creator'], indata['rootcause']
        x = Product(description="test pipeline product",
                    creator=runner, rootCause=cause,
                    instrument="hello", modelName="you know what!")
        x['theAnswer'] = GenericDataset(
            data=res['outfile'], description='result from runPTS command')
        x.type = 'test'
        x.history = History()
        now = time.time()
        x.creationDate = FineTime1(datetime.datetime.fromtimestamp(now))
        return x

    return run(d, processinput, processoutput)


def run(d, processinput=None, processoutput=None):
    """  Generates a product by running script defined in the config under 'run'. Execution on the server host is in the pnshome directory and run result and status are returned.
    """

    global lupd

    pnsh = pc['paths']['pnshome']
    p = checkpath(pnsh)
    if p is None:
        abort(401)

    pi = checkpath(pc['paths']['inputdir'])
    po = checkpath(pc['paths']['outputdir'])
    if pi is None or po is None:
        abort(401)

    indata = deserializeClassID(d)
    logger.debug(indata)

    try:
        if processinput is not None:
            processinput(d, indata)
        else:
            r1 = {'contents': indata['input'].toString(),
                  'mode': 'w+'}
            p = indata['input'].meta['pointing'].value.components
            r2 = {'contents': str(p[0]) + ' ' + str(p[1]),
                  'mode': 'w+'}
            data = {pc['paths']['inputfiles'][0]: r1,
                    pc['paths']['inputfiles'][1]: r2}
            defaultprocessinput(data)
    except Exception as e:
        return -1,  str(e) + trbk(e)

    ######### run PTS ########
    if hasattr(indata, '__iter__') and 'timeout' in indata:
        timeout = indata['timeout']
    else:
        timeout = pc['timeout']

    stat = _execute(pc['scripts']['run'], timeout=timeout)
    if stat['returncode'] != 0:
        return stat['returncode'], stat

    ######### output ########
    try:
        if processoutput is not None:
            x = processoutput(d, indata)
        else:
            n = len(pc['paths']['outputfiles'])
            fm = dict(zip(pc['paths']['outputfiles'], ['r'] * n))
            x = defaultprocessoutput(fm)
    except Exception as e:
        return -1, str(e) + trbk(e)

    return x, stat


def calc(d):
    """ generates result product directly using data on PNS.
    """
    return 0, ''


def genposttestprod(d):
    """ generate post test product.
    put the 1st input (see maketestdata in test_pns.py)
    parameter to metadata
    and 2nd to the product's dataset
    """

    indata = deserializeClassID(d)
    logger.debug(indata)

    runner, cause = indata['creator'], indata['rootcause']
    x = Product(description="This is my product example",
                creator=runner, rootCause=cause,
                instrument="MyFavourite", modelName="Flight")
    input = indata['input']
    pname, pv = list(input.meta.items())[0]
    dname, dv = list(input.getDataWrappers().items())[0]
    # print(im == dv)  # this should be true
    x.meta[pname] = pv
    x[dname] = dv
    # add some random dataset for good measure
    s1 = TableDataset(data=[('col1', [1, 4.4, 5.4E3], 'eV'),
                            ('col2', [0, 43.2, 2E3], 'cnt')
                            ])
    x['spectrum'] = s1
    now = time.time()
    x.creationDate = FineTime1(datetime.datetime.fromtimestamp(now))
    x.type = 'test'
    x.history = History()
    return x, ''


def dosleep(indata, ops):
    """ run 'sleep [ops]' in the OS. ops is 3 if not given.
    """
    try:
        t = float(ops)
    except ValueError as e:
        t = 3
    if hasattr(indata, '__iter__') and 'timeout' in indata:
        timeout = indata['timeout']
    else:
        timeout = pc['timeout']

    stat = _execute(['sleep', str(t)], timeout=timeout)
    if stat['returncode'] != 0:
        return stat['returncode'], stat
    return 0, stat


def filesin(dir):
    """ returns names and contents of all files in the dir, 'None' if dir not existing. """

    if not isdir(dir):
        return None, dir + ' does not exist.'
    result = {}
    for f in listdir(dir):
        fn = join(dir, f)
        if isfile(fn):
            with open(fn, 'r') as f:
                result[fn] = f.read()
    return result, ''


@app.route(pc['baseurl'] + '/<string:cmd>', methods=['GET'])
def getinfo(cmd):
    ''' returns init, config, run input, run output.
    '''
    logger.debug('getr %s' % (cmd))

    msg = ''
    ts = time.time()
    try:
        if cmd == 'init':
            with open(pc['scripts']['init'][0], 'r') as f:
                result = f.read()
        elif cmd == 'config':
            with open(pc['scripts']['config'][0], 'r') as f:
                result = f.read()
        elif cmd == 'run':
            with open(pc['scripts']['run'][0], 'r') as f:
                result = f.read()
        elif cmd == 'clean':
            with open(pc['scripts']['clean'][0], 'r') as f:
                result = f.read()
        elif cmd == 'input':
            result, msg = filesin(pc['paths']['inputdir'])
        elif cmd == 'output':
            result, msg = filesin(pc['paths']['outputdir'])
        elif cmd == 'pnsconfig':
            result, msg = pc, ''
        else:
            result, msg = -1, cmd + ' is not valid.'
    except Exception as e:
        result, msg = -1, str(e) + trbk(e)
    w = {'result': result, 'message': msg, 'timestamp': ts}

    s = serializeClassID(w)
    logger.debug(s[:] + ' ...')
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


# import requests
# from http.client import HTTPConnection
# HTTPConnection.debuglevel = 1

@auth.verify_password
def verify(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if not (username and password):
        return False
    return username == pc['node']['username'] and password == pc['node']['password']


@app.route(pc['baseurl'] + '/<string:cmd>', methods=['POST'])
@app.route(pc['baseurl'] + '/<string:cmd>/<string:ops>', methods=['POST'])
def calcresult(cmd, ops=''):

    logger.debug('pos ' + cmd + ' ' + ops)
    d = request.get_data()
    if cmd == 'calc':
        result, msg = calc(d)
    elif cmd == 'testcalc':
        # see test_post() in test_all.py
        result, msg = genposttestprod(d)
    elif cmd == 'echo':
        # see test_mirror() in test_all.py
        indata = deserializeClassID(d)
        logger.debug(indata)
        result, msg = indata, ''
    else:
        # the following need to be locked
        pnsh = pc['paths']['pnshome']
        # check if it is locked with timeout==0
        lock = filelock.FileLock(pnsh + '/.lock', timeout=0)
        try:
            lock.acquire()
        except filelock.Timeout as e:
            logger.debug('busy')
            abort(409, 'pns is busy')
        with lock:
            if cmd == 'run':
                result, msg = run(d)
            elif cmd == 'testrun':
                # see test_testrun() in test_all.py
                result, msg = testrun(d)
            elif cmd == 'sleep':
                # sleep in the OS for ops seconds
                indata = deserializeClassID(d)
                result, msg = dosleep(indata, ops)
            else:
                logger.error(cmd)
                abort(400)
                result = None
    ts = time.time()
    w = {'result': result, 'message': msg, 'timestamp': ts}
    s = serializeClassID(w)
    logger.debug(s[: 160] + ' ...')
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route(pc['baseurl'] + '/<string:cmd>', methods=['PUT'])
@app.route(pc['baseurl'] + '/<string:cmd>/<ops>', methods=['PUT'])
def setup(cmd, ops=''):
    """ PUT is used to initialize or configure the Processing Task Software
    (PST).
    """

    d = request.get_data()
    # logger.debug(d)

    # the following need to be locked
    pnsh = pc['paths']['pnshome']
    # check if it is locked with timeout==0
    lock = filelock.FileLock(pnsh + '/.lock', timeout=0)
    try:
        lock.acquire()
    except filelock.Timeout as e:
        logger.debug('busy')
        abort(409, 'pns is busy')
    with lock:
        if cmd == 'init':
            try:
                result, msg = initPTS(d)
            except Exception as e:
                msg = str(e) + trbk(e)
                logger.error(msg)
                result = -1
        elif cmd == 'config':
            result, msg = configPTS(d)
        elif cmd == 'pnsconf':
            result, msg = configPNS(d)
        elif cmd == 'upload':
            if ops not in pc['scripts'].keys():
                logger.error('invalid operation type ' + ops)
                abort(400)
                result = None
            result, msg = uploadScript(ops, d)
        elif cmd == 'testinit':
            result, msg = testinit(d)
        else:
            logger.error(cmd)
            abort(400)
    ts = time.time()
    w = {'result': result, 'message': msg, 'timestamp': ts}
    s = serializeClassID(w)
    # logger.debug(s[:] + ' ...')
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route(pc['baseurl'] + '/<string:cmd>', methods=['DELETE'])
def cleanup(cmd):
    """ DELETE is used to clean up the Processing Task Software
    (PST) to its initial configured state.
    """

    d = request.get_data()
    # print('&&&&&&&& ' + str(d))
    if cmd == 'clean':
        try:
            result, msg = cleanPTS(d)
        except Exception as e:
            msg = str(e) + trbk(e)
            logger.error(msg)
            result = None
    else:
        logger.error(cmd)
        abort(400)
        result = None
    ts = time.time()
    w = {'result': result, 'message': msg, 'timestamp': ts}
    s = serializeClassID(w)
    logger.debug(s[:] + ' ...')
    resp = make_response(s)
    resp.headers['Content-Type'] = 'application/json'
    return resp


APIs = {'GET':
        {'func': 'getinfo',
         'cmds': {'init': 'the initPTS file', 'config': 'the configPTS file',
                  'run': 'the file running PTS', 'clean': 'the cleanPTS file',
                  'input': filesin, 'output': filesin,
                  'pnsconfig': 'PNS configuration'}
         },
        'PUT':
        {'func': 'setup',
         'cmds': {'init': initPTS, 'config': configPTS, 'pnsconf': configPNS, 'testinit': testinit}
         },
        'POST':
        {'func': 'calcresult',
         'cmds': {'calc': calc, 'testcalc': genposttestprod,
                  'run': run, 'testrun': testrun,
                  'echo': 'Echo',
                  'sleep': (dosleep,  dict(ops='3'))}
         },
        'DELETE':
        {'func': 'cleanup',
         'cmds': {'clean': cleanPTS}
         }}


def makepublicAPI(ops):
    api = []
    o = APIs[ops]
    for cmd in o['cmds'].keys():
        cs = o['cmds'][cmd]
        if not issubclass(cs.__class__, tuple):  # e.g. 'run':run
            c = cs
            kwds = {}
        else:  # e.g. 'sleep': (dosleep, dict(ops='1'))
            c = cs[0]
            kwds = cs[1]
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


@app.route(pc['baseurl'] + '/', methods=['GET'])
@app.route(pc['baseurl'] + '/api', methods=['GET'])
def get_apis():
    logger.debug('APIs %s' % (APIs.keys()))
    ts = time.time()
    l = [(a, makepublicAPI(a)) for a in APIs.keys()]
    w = {'APIs': dict(l), 'timestamp': ts}
    logger.debug('ret %s' % (str(w)[:100] + ' ...'))
    return jsonify(w)


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
def not_found(error):
    ts = time.time()
    w = {'error': 'Conflict. Updating.',
         'message': str(error), 'timestamp': ts}
    return make_response(jsonify(w), 409)
