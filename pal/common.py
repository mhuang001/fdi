# -*- coding: utf-8 -*-
from collections import ChainMap
import builtins
import filelock
import logging
import os
import gc

# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))

from .urn import Urn
from dataset.deserialize import deserializeClassID


def getJsonObj(fp, usedict=False):

    with open(fp, 'r') as f:
        stri = f.read()
    # ret = json.loads(stri, parse_float=Decimal)
    # ret = json.loads(stri, cls=Decoder,
    #               object_pairs_hook=collections.OrderedDict)
    #lgb = ChainMap(locals(), globals(), vars(builtins))
    lgb = None
    ret = deserializeClassID(stri, lgb=lgb, usedict=usedict)
    logger.debug(str(ret)[:160] + '...')
    return ret


def getObjectbyId(idn, lgbv):
    """ lgb is from deserializing caller's globals().values()
    locals().values() and built-ins
    """
    v = lgbv
    for obj in v:
        if id(obj) == idn:
            return obj
    raise ValueError("Object not found by id %d." % (idn))


def getProductObject(urn, lgb=None):
    """ Returns a product from URN. returns object.
    """
    poolname, resourcecn, indexs, scheme, place, poolpath = Urn.parseUrn(
        urn)
    if scheme == 'file':
        lock = filelock.FileLock(poolpath + '/lock')
        lock.acquire()
        try:
            p = getJsonObj(poolpath + '/' + resourcecn + '_' + indexs)
        except Exception as e:
            raise e
        finally:
            lock.release()
    elif scheme == 'mem':
        processid = int(poolpath.rsplit('/', maxsplit=1)[1])
        if processid != os.getpid():
            raise ValueError('vannot restore from ' +
                             urn + ' of another process')
        idn = int(indexs)
        # logger.debug(urn)
        if lgb is None:
            # lgb = ChainMap(locals(), globals())  # , vars(builtins))
            lgbv = gc.get_objects()
        else:
            raise Exception()
            lgbv = lgb.values()
        if 0:
            print(lgb['image'])
            for k, v in lgb.items():
                if issubclass(v.__class__, Product):
                    logger.debug(k + ': ' + str(type(v)))
                    logger.debug(': ' + str(v))
        p = getObjectbyId(idn, lgbv=lgbv)
    return p


def getClass1(name):
    """
    """
    return globals()[name]
