from fdi.dataset.dataset import ArrayDataset
import itertools
import random
import timeit
from fdi.pal.mempool import MemPool
from fdi.pal.poolmanager import PoolManager, DEFAULT_MEM_POOL
from fdi.utils.common import trbk
from fdi.pal.common import getProductObject
from fdi.pal.context import Context, MapContext
from fdi.pal.productref import ProductRef
from fdi.pal.productstorage import ProductStorage
from fdi.pal.urn import Urn, parseUrn, makeUrn
from fdi.pal.localpool import LocalPool
from fdi.dataset.deserialize import deserializeClassID
from fdi.dataset.product import Product
from fdi.dataset.eq import deepcmp
import copy
import traceback
from pprint import pprint
import json
import shutil
import os

from os import path as op
import glob
import yaml

import sys
# print([(k, v) for k, v in globals().items() if '__' in k])
import pdb

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
else:
    PY3 = False

if __name__ == '__main__' and __package__ is None:
    pass
else:
    # This is to be able to test w/ or w/o installing the package
    # https://docs.python-guide.org/writing/structure/
    from .pycontext import fdi

    from .logdict import logdict
    import logging
    import logging.config
    # create logger
    logging.config.dictConfig(logdict)
    logger = logging.getLogger()
    logger.debug('%s logging level %d' %
                 (__name__, logger.getEffectiveLevel()))
    logging.getLogger("filelock").setLevel(logging.WARNING)


# from products.QSRCLIST_VT import QSRCLIST_VT


def checkjson(obj):
    """ seriaizes the given object and deserialize. check equality.
    """

    # dbg = True if issubclass(obj.__class__, Product) else False
    dbg = False

    if hasattr(obj, 'serialized'):
        js = obj.serialized()
    else:
        js = json.dumps(obj)

    if dbg:
        print('*************** checkjsom ' + obj.__class__.__name__ +
              ' serialized: ************\n')
        print(js)
        print('*************************')
    des = deserializeClassID(js, debug=dbg)
    if dbg:
        if hasattr(des, 'meta'):
            print('moo ' + str((des.meta.listeners)))
        print('*********** checkjson deserialized ' + str(des.__class__) +
              '***********\n')
        pprint(des)

        # js2 = json.dumps(des, cls=SerializableEncoder)
        # pprint('******** des     serialized: **********')
        # pprint(js)

        r = deepcmp(obj, des)
        print('*************** deepcmp ***************')
        if r is not None:
            print(r + '\nOBJ ' + yaml.dump(obj) + '\nDES ' + yaml.dump(des))
        else:
            print('identical')

    if 0 and issubclass(obj.__class__, Product):
        obj.meta.listeners = []
        des.meta.listeners = []
    assert obj == des, deepcmp(obj, des) + '\nOBJ ' + \
        yaml.dump(obj) + '\nDES ' + yaml.dump(des)
    return des


def checkgeneral(v):
    # can always add attributes
    t = 'random'
    v.testattr = t
    assert v.testattr == t
    try:
        m = v.notexists
    except AttributeError as e:
        assert str(e).split()[-1] == "'notexists'", traceback.print_exc()
    except:
        traceback.print_exc()
        assert false


def test_Urn():
    prd = Product(description='pal test')
    a1 = 'file'      # scheme
    c1, c2 = 's:', '/d'
    a2 = c1            # place
    b1, b2, b3 = '/b', '/tmp/foo', '/c'
    a3 = b1 + b2 + b3
    a4 = prd.__class__.__name__
    a5 = 43
    s = a1 + '://' + a2   # file://s:
    p = s + a3
    r = a4 + ':' + str(a5)
    rp = a4 + '_' + str(a5)
    u = 'urn:' + p + ':' + r

    # utils
    assert parseUrn(u) == (p, a4, str(a5), a1, a2, a2 + a3)
    poolname, resourceclass, serialnumstr, scheme, place, poolpath = parseUrn(
        'urn:file://c:/tmp/mypool:proj1.product:322')
    assert poolname == 'file://c:/tmp/mypool'
    assert resourceclass == 'proj1.product'
    assert place == 'c:'
    assert poolpath == 'c:/tmp/mypool'
    poolname, resourceclass, serialnumstr, scheme, place, poolpath = parseUrn(
        'urn:https://127.0.0.1:5000/tmp/mypool:proj1.product:322')
    assert poolname == 'https://127.0.0.1:5000/tmp/mypool'
    assert resourceclass == 'proj1.product'
    assert place == '127.0.0.1:5000'
    assert poolpath == '/tmp/mypool'

    # constructor
    # urn only
    v = Urn(urn=u)
    assert v.getScheme() == a1
    assert v.getPlace() == a2
    assert v.getPoolId() == p  #
    assert v.getUrnWithoutPoolId() == r
    assert v.getFullPath(u) == a2 + a3 + '/' + rp  # s:/b/tmp/foo/c
    assert v.getIndex() == a5
    assert v.getUrn() == u
    # urn with pool
    v = Urn(cls=prd.__class__, pool=p, index=a5)
    assert v.getScheme() == a1
    assert v.getFullPath(u) == a2 + a3 + '/' + rp  # s:/b/tmp/foo/c
    # urn with storage that does not match urn
    try:
        v = Urn(urn=u, cls=prd.__class__, pool=p, index=a5)
    except Exception as e:
        assert issubclass(e.__class__, ValueError)
    # no-arg constructor
    v = Urn()
    v.urn = u
    assert v.getScheme() == a1
    assert v.getFullPath(u) == a2 + a3 + '/' + rp  # s:/b/tmp/foo/c

    # access
    assert v.getUrn() == v.urn
    assert v.getPool() == v.pool
    assert v.getTypeName() == a4
    assert v.getPlace() == v.place

    checkjson(v)


def cleanup(direc):
    """ remove pool from disk and memory"""
    if op.exists(direc):
        try:
            # print(os.stat(direc))
            shutil.rmtree(direc)
        except Exception as e:
            print(str(e) + ' ' + trbk(e))
            raise(e)
        assert not op.exists(direc)
    # remove existing pools in memory
    PoolManager.getPool(DEFAULT_MEM_POOL).removeAll()
    PoolManager.removeAll()


def test_PoolManager():
    defaultpoolpath = '/tmp/pool'
    defaultpool = 'file://' + defaultpoolpath
    cleanup(defaultpoolpath)
    pm = PoolManager()
    assert pm.size() == 0
    pool = pm.getPool(defaultpool)
    assert pm.size() == 1
    # print('GlobalPoolList#: ' + str(id(pm.getMap())) + str(pm))
    pm.removeAll()
    assert pm.size() == 0


def checkdbcount(n, poolurn, prodname, currentSN=-1):
    """ count files in pool and entries in class db.
    n, currentSN: expected number of prods and currentSN in pool for products named prodname
    """

    poolname, rc, sns, scheme, place, path = parseUrn(poolurn)
    if scheme == 'file':
        assert sum(1 for x in glob.glob(
            op.join(path, prodname + '*[0-9]'))) == n
        cp = op.join(path, 'classes.jsn')
        if op.exists(cp) or n != 0:
            with open(cp, 'r') as fp:
                cread = json.load(fp)
                if currentSN == -1:
                    assert cread[prodname]['currentSN'] == currentSN
                    # number of items is n
                assert len(cread[prodname]['sn']) == n
    elif scheme == 'mem':
        mpool = PoolManager.getPool(poolname).getPoolSpace()
        ns = [n for n in mpool if prodname + '_' in n]
        assert len(ns) == n, len(ns)
        if currentSN == -1:
            assert mpool['classes'][prodname]['currentSN'] == currentSN
        # for this class there are  how many prods
        assert len(mpool['classes'][prodname]['sn']) == n
    else:
        assert False, 'bad pool scheme'


def test_ProductRef():
    defaultpoolpath = '/tmp/pool'
    defaultpool = 'file://' + defaultpoolpath
    cleanup(defaultpoolpath)
    prd = Product()
    a1 = 'file'
    a2 = ''
    a3 = defaultpoolpath
    a4 = prd.__class__.__name__
    a5 = 0
    s = a1 + '://' + a2   # file://s:
    p = s + a3  # a pool URN
    r = a4 + ':' + str(a5)  # a resource
    u = 'urn:' + p + ':' + r    # a URN

    # in memory
    # A productref created from a single product will result in a memory pool urn, and the metadata won't be loaded.
    v = ProductRef(prd)
    # only one prod in memory pool
    checkdbcount(1, DEFAULT_MEM_POOL, a4, 0)
    assert v.urn == 'urn:mem:///default:' + a4 + ':' + str(0)
    assert v.meta is None
    assert v.product == prd
    cleanup(defaultpoolpath)

    # construction
    ps = ProductStorage(p)
    prd = Product()
    rfps = ps.save(prd)
    pr = ProductRef(urn=rfps.urnobj, poolurn=p)
    assert rfps == pr
    assert rfps.getMeta() == pr.getMeta()
    uobj = Urn(urn=u)
    assert pr.urnobj == uobj
    # This does not obtain metadata
    pr = ProductRef(urn=rfps.urnobj)
    assert rfps == pr
    assert rfps.getMeta() != pr.getMeta()
    assert pr.urnobj == uobj
    assert pr.getStorage() == ps
    assert rfps.getStorage() is not None
    # load from a storage.
    pr = ps.load(u)
    assert rfps == pr
    assert rfps.getMeta() == pr.getMeta()
    assert pr.getStorage() == rfps.getStorage()

    # parent
    # nominal ops
    b1 = Product(description='abc')
    b2 = MapContext(description='3c273')
    pr.addParent(b1)
    pr.addParent(b2)
    assert b1 in list(pr.parents)
    assert b2 in list(pr.parents)
    pr.removeParent(b1)
    assert b1 not in list(pr.parents)
    # access
    assert pr.urnobj.getTypeName() == a4
    assert pr.urnobj.getIndex() == a5
    # this is tested in ProdStorage
    # assert pr.product == p

    checkjson(pr)


def test_ProductStorage():
    defaultpoolpath = '/tmp/pool'
    defaultpool = 'file://' + defaultpoolpath
    cleanup(defaultpoolpath)

    x = Product(description="This is my product example",
                instrument="MyFavourite", modelName="Flight")
    pcq = x.__class__.__name__
    # constructor
    # default pool
    ps = ProductStorage()
    p1 = ps.getPools()[0]
    assert p1 == defaultpool
    pspool = ps.getPool(p1)
    assert len(pspool.getProductClasses()) == 0
    # construct a storage with a pool
    ps2 = ProductStorage(defaultpool)
    assert ps.getPools() == ps2.getPools()

    # register pool
    # with a storage that already has a pool
    newpoolpath = '/tmp/newpool'
    newpoolname = 'file://' + newpoolpath
    cleanup(newpoolpath)

    ps2.register(newpoolname)
    assert op.exists(newpoolpath)
    assert len(ps2.getPools()) == 2
    assert ps2.getPools()[1] == newpoolname

    # save
    ref = ps.save(x)
    # ps has 1 prod
    assert ref.urn == 'urn:' + defaultpool + ':' + pcq + ':0'
    checkdbcount(1, defaultpool, pcq, 0)

    # save more
    # one by one
    q = 3
    x2, ref2 = [], []
    for d in range(q):
        tmp = Product(description='x' + str(d)
                      ) if d > 0 else MapContext(description='x0')
        x2.append(tmp)
        ref2.append(ps.save(tmp, tag='t' + str(d)))
    checkdbcount(q, defaultpool, pcq, q - 1)
    checkdbcount(1, defaultpool, MapContext.__name__, 0)
    # save many in one go
    m, x3 = 2, []
    n = q + m
    for d in range(q, n):
        tmp = Product(description='x' + str(d))
        x3.append(tmp)
    ref2 += ps.save(x3, tag='all-tm')  # ps has n+1 prods
    x2 += x3  # there are n prods in x2
    # check refs
    assert len(ref2) == n
    checkdbcount(n, defaultpool, pcq, n)
    checkdbcount(1, defaultpool, MapContext.__name__, 0)

    # tags
    ts = ps.getAllTags()
    assert len(ts) == q + 1
    ts = ps.getTags(ref2[0].urn)
    assert len(ts) == 1
    assert ts[0] == 't0'
    u = ps.getUrnFromTag('all-tm')
    assert len(u) == m
    assert u[0] == ref2[q].urn

    # multiple storages pointing to the same pool will get exception
    try:
        ps2 = ProductStorage()
    except Exception as e:
        pass
    else:
        assert 1  # False

    # read HK
    # copy default pool data in memory
    ps1 = copy.deepcopy(pspool)
    # rename the pool
    cp = defaultpoolpath + '_copy'
    cleanup(cp)
    # make a copy of the old pool on disk
    shutil.copytree(defaultpoolpath, cp)
    ps2 = ProductStorage(pool='file://' + cp)
    # two ProdStorage instances have the same DB
    p2 = ps2.getPool(ps2.getPools()[0])
    assert deepcmp(ps1._urns, p2._urns) is None
    assert deepcmp(ps1._tags, p2._tags) is None
    assert deepcmp(ps1._classes, p2._classes) is None

    # access resource
    checkdbcount(n, defaultpool, pcq, n)
    checkdbcount(1, defaultpool, MapContext.__name__, 0)
    # get ref from urn
    pref = ps.load(ref2[n - 2].urn)
    assert pref == ref2[n - 2]
    # actual product
    # print(pref._product)
    assert pref.product == x2[n - 2]
    # from tags

    # removal by reference urn
    # print(ref2[n - 2].urn)
    ps.remove(ref2[n - 2].urn)
    # files are less
    # DB shows less in record
    # current serial number not changed
    # number of items decreased by 1
    checkdbcount(n - 1, defaultpool, pcq, n)
    checkdbcount(1, defaultpool, MapContext.__name__, 0)

    # clean up a pool
    ps.wipePool(defaultpool)
    checkdbcount(0, defaultpool, pcq)
    assert len(ps.getPool(defaultpool)._urns) == 0


def test_Context():
    c1 = Context(description='1')
    c2 = Context(description='2')
    assert Context.isContext(c2.__class__)
    try:
        assert c1.isValid()
    except NotImplementedError as e:
        pass
    else:
        assert False

    # dirtiness
    # assert not c1.hasDirtyReferences('ok')
    #


def test_MapContext():
    # doc
    image = Product(description="hi")
    spectrum = Product(description="there")
    simple = Product(description="everyone")

    context = MapContext()
    context.refs.put("x", ProductRef(image))
    context.refs.put("y", ProductRef(spectrum))
    context.refs.put("z", ProductRef(simple))
    assert context.refs.size() == 3
    assert context.refs.get('x').product.description == 'hi'
    assert context.refs.get('y').product.description == 'there'
    assert context.refs.get('z').product.description == 'everyone'

    product4 = Product(description="everybody")
    context.refs.put("y", ProductRef(product4))
    product5 = Product(description="here")
    context.refs.put("a", ProductRef(product5))

    assert context.refs.get('x').product.description == 'hi'
    assert context.refs.get('y').product.description == 'everybody'
    assert context.refs.get('z').product.description == 'everyone'
    assert context.refs.get('a').product.description == 'here'

    # access
    c1 = MapContext()
    # syntax 1. refs is a property to MapContext
    c1.refs.put("x", ProductRef(image))
    c2 = MapContext()
    # syntax 2  # put == set
    c2.refs.set("x", ProductRef(image))
    # assert c1 == c2, deepcmp(c1, c2)
    c3 = MapContext()
    # syntax 3 # refs is a composite so set/get = []
    c3.refs["x"] = ProductRef(image)
    # assert c3 == c2
    assert c3.refs['x'].product.description == 'hi'
    c4 = MapContext()
    # syntax 4. refs is a member in a composite (Context) so set/get = []
    c4['refs']["x"] = ProductRef(image)
    # assert c3 == c4
    assert c4['refs']['x'].product.description == 'hi'

    # stored prod
    defaultpoolpath = '/tmp/pool'
    defaultpool = 'file://' + defaultpoolpath
    # create a prooduct
    x = Product(description='in store')
    # remove existing pools in memory
    PoolManager().removeAll()
    # create a product store
    pstore = ProductStorage()
    assert len(pstore.getPools()) == 1
    assert pstore.getWritablePool() == defaultpool
    assert op.isdir(defaultpoolpath)
    # clean up possible garbage of previous runs
    pstore.wipePool(defaultpool)
    assert op.isdir(defaultpoolpath)
    assert sum([1 for x in glob.glob(op.join(defaultpoolpath, '*'))]) == 0
    # save the product and get a reference
    prodref = pstore.save(x)
    # has the ProductStorage
    assert prodref.getStorage() == pstore
    # has the pool
    assert prodref._poolurn == defaultpool
    # returns the product
    assert prodref.product == x
    # create an empty mapcontext
    mc = MapContext()
    # put the ref in the context.
    # The manual has this syntax mc.refs.put('xprod', prodref)
    # but I like this for doing the same thing:
    mc['refs']['xprod'] = prodref
    # get the urn
    urn = prodref.urn
    assert issubclass(urn.__class__, str)
    # re-create a product only using the urn
    #newp = getProductObject(urn)
    newp = ProductRef(urn).product
    # the new and the old one are equal
    assert newp == x
    # parent is set
    assert prodref.parents[0] == mc
    # re-create a product only using the urn 2
    newref = pstore.load(urn)
    newp2 = newref.product
    # the new and the old one are equal
    assert newp2 == x

    des = checkjson(mc)
    # print(type(des['refs']))
    # print('&&&&&& ' + des.refs.serialized(indent=4) + ' %%%%%%')
    # print(yaml.dump(des))

    newx = des['refs']['xprod'].product
    assert newx == x

    # remove refs
    del mc.refs['xprod']
    assert mc.refs.size() == 0
    assert len(prodref.parents) == 0
    # another way to remove
    des.refs.pop('xprod')
    assert des.refs.size() == 0
    assert len(prodref.parents) == 0
    # clear all
    prodref2 = pstore.save(Product())
    mc.refs['a'] = prodref
    mc.refs['b'] = prodref2
    assert mc.refs.size() == 2
    mc.refs.clear()
    assert mc.refs.size() == 0

    # URN of an object in memory
    urn = ProductRef(x).urn
    newp = PoolManager.getPool(DEFAULT_MEM_POOL).loadProduct(urn)
    # the new and the old one are equal
    assert newp == x

    # realistic scenario


def test_realistic():
    # remove existing pools in memory
    PoolManager().removeAll()
    poolpath = '/tmp/realpool'
    poolname = 'file://'+poolpath
    # clean up possible garbage of previous runs. use class method to avoid reading pool hk info during ProdStorage initialization.
    LocalPool.wipe(poolpath)
    pstore = ProductStorage(pool=poolname)  # on disk

    p1 = Product(description='p1')
    p2 = Product(description='p2')
    map1 = MapContext(description='real map1')
    pref1 = ProductRef(p1)  # in memory
    pref2 = pstore.save(p2)  # on disk
    assert map1['refs'].size() == 0  # do not use len() due to classID
    assert len(pref1.parents) == 0
    assert len(pref2.parents) == 0
    # add a ref to the contex
    map1['refs']['prd1'] = pref1
    assert map1['refs'].size() == 1
    assert len(pref1.parents) == 1
    assert pref1.parents[0] == map1
    # add the second one
    map1['refs']['prd2'] = pref2
    assert map1['refs'].size() == 2
    assert len(pref2.parents) == 1
    assert pref2.parents[0] == map1
    assert pref1.parents[0] == map1
    # remove a ref
    del map1['refs']['prd1']
    assert map1.refs.size() == 1
    assert len(pref1.parents) == 0
    # add ref2 to another map
    map2 = MapContext(description='real map2')
    map2.refs['also2'] = pref2
    assert map2['refs'].size() == 1
    # two parents
    assert len(pref2.parents) == 2
    assert pref2.parents[1] == map2


def f(n):
    return list(itertools.repeat(random.random(), n))


def rands(n):
    return [random.random() for i in range(n)]


def h(n):
    return [random.random()] * n


def speed():
    m = 10000
    print(timeit.timeit('[func(%d) for func in (rands,)]' % m,
                        globals=globals(), number=1))
    a = ArrayDataset(rands(m))
    p = Product(description="product example",
                instrument="Favourite", modelName="Flight")
    p['array'] = a
    PoolManager().removeAll()
    # create a product store
    pool = 'file:///tmp/perf'
    pstore = ProductStorage(pool)
    # clean up possible garbage of previous runs
    pstore.wipePool(pool)
    # in memory
    print(timeit.timeit('ref1 = ProductRef(p)',
                        globals=globals().update(locals()), number=1))
    pref2 = pstore.save(p)  # on disk


def running(t):
    print('running ' + str(t))
    t()


if __name__ == '__main__' and __package__ is None:
    speed()
    exit()
    running(test_ProductRef)
    running(test_ProductRef)
    running(test_MapContext)
    running(test_Urn)
    # running(test_MapRefsDataset)
    running(test_PoolManager)
    running(test_ProductStorage)
    running(test_Context)
    # pdb.set_trace()
