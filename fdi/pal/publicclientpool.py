# -*- coding: utf-8 -*-

from fdi.httppool.session import requests_retry_session
from fdi.dataset.product import Product, BaseProduct
from fdi.dataset.serializable import serialize
from fdi.pal.poolmanager import PoolManager
from fdi.pal.productpool import ManagedPool, populate_pool2
from fdi.pal.productref import ProductRef
from fdi.pal.productstorage import ProductStorage
from fdi.pal.urn import makeUrn, parse_poolurl, Urn, parseUrn
from fdi.pns.public_fdi_requests import read_from_cloud, load_from_cloud, delete_from_server
from fdi.utils.common import fullname, lls, trbk
from fdi.utils.getconfig import getConfig

import logging
import os
from itertools import chain
import sys

logger = logging.getLogger(__name__)
pcc = getConfig()

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
    strset = str
else:
    PY3 = False
    strset = (str, unicode)

"""
Cloud apis classification:
#/%E9%85%8D%E7%BD%AE%E7%AE%A1%E7%90%86
DOC: http://123.56.102.90:31702/api/swagger-ui.html
Problem:
1. No class shown in storage/info API
2. No pattern for pool path, API use poolname+random name instead of pool <scheme>://<place><poolpath>/<poolname>
3. getMetaByUrn(self, urn, resourcetype=None, index=None) What's means resourcetype and index?
"""


def get_Values_From_A_list_of_dicts(res, what):
    """"If the list only has 1 element, return the value instead of the list """
    if not res:
        return None
    if len(res) > 1:
        return [r.get(what, None) for r in res]
    else:
        return res[0].get(what, None)


class PublicClientPool(ManagedPool):
    def __init__(self,  auth=None, client=None, **kwds):
        """ creates file structure if there isn't one. if there is, read and populate house-keeping records. create persistent files if not exist.

        Parameters
        ----------
        auth : tuple, HTTPBasicAuth, or Authorization
            Authorization for remote pool.
        client : Request or Wrapper
            Mainly used for testing with mock server.
        **kwds :

        Returns
        -------

        """
        # print(__name__ + str(kwds))
        super().__init__(**kwds)
        self.auth = auth
        if client is None:
            client = requests_retry_session()
        self.client = client
        self.getToken()
        self.poolInfo = None

    def setup(self):
        """ Sets up HttpPool interals.

        Make sure that self._poolname and self._poolurl are present.
        """

        if super().setup():
            return True

        return False

    def setPoolurl(self, poolurl):
        """ Replaces the current poolurl of this pool.
            For cloud pool, there are also self._cloudpoolpath and self._cloudpoolname
            csdb:///csdb_test_pool
            self._poolpath, self._scheme, self._poolname = '', 'csdb', 'csdb_test_pool'
            self._cloudpoolpath = /csdb_test_pool
        """
        s = (not hasattr(self, '_poolurl') or not self._poolurl)
        self._poolpath, self._scheme, self._place, \
            self._poolname, self._username, self._password = \
            parse_poolurl(poolurl)
        if self._scheme == '' or self._scheme == None:
            self._scheme = 'csdb'
        self._cloudpoolpath = self._poolpath + '/' + self._poolname
        self._poolurl = poolurl
        # call setup only if poolurl was None
        if s:
            self.setup()

    def getPoolpath(self):
        if self._cloudpoolpath:
            return self._cloudpoolpath
        else:
            return self._poolpath

    def getToken(self):
        """Get CSDB acces token.

        Returns
        -------
        str
            Saved or newly gotten token.

        Raises
        ------
        RuntimeError
            Could not get new token.

        """

        self.token = pcc['cloud_token']
        tokenMsg = read_from_cloud(
            'verifyToken', token=self.token, client=self.client)
        if tokenMsg.get('code') != 0:
            logger.debug('Cloud token %s to be updated.' % self.token[:5])
            tokenMsg = read_from_cloud('getToken', client=self.client)
            if tokenMsg['data']:
                self.token = tokenMsg['data']['token']
                logger.debug('Cloud token %s updated.' % self.token[:5])
            else:
                raise RuntimeError('Update cloud token failed: ' +
                                   tokenMsg['msg'])
        return self.token

    def poolExists(self):
        res = read_from_cloud(
            'existPool', poolname=self.poolname, token=self.token)
        if res['msg'] == 'success':
            return True
        else:
            return False

    def restorePool(self):
        res = read_from_cloud(
            'restorePool', poolname=self.poolname, token=self.token)
        if res['msg'] == 'success':
            return True
        else:
            return False

    def createPool2(self):
        res = read_from_cloud(
            'createPool', poolname=self.poolname, token=self.token)

        if res['msg'] == 'success':
            return True, res
        elif res['msg'] == 'The storage pool already exists. Change the storage pool name':
            return True, res
        elif res['msg'] == 'The storage pool name already exists in the recycle bin. Change the storage pool name':
            raise ValueError(
                res['msg'] + ', please restore pool ' + self.poolname + ' firstly.')
        else:
            return False, res

    def createPool(self):
        return self.createPool2()[0]

    def getPoolInfo(self, update_hk=True):
        """
        Pool schema 1.0 consisted of three maps: classes, urns and tags
        data:. See productpool::ManagedPool::saveOne
            poolname :
                _classes= {productTypeName: {currentSn:csn, sn=[]}}
                _urns= [{urn: tags[]}]
                _tags= {urns:[]}
        """
        res = read_from_cloud(
            'infoPool', pools=self.poolname, token=self.token)
        if res['code'] == 0:
            rdata = res['data']
            if rdata:
                self.poolInfo = rdata
                if self._poolname in rdata:
                    if update_hk:
                        for urn, tags in rdata[self._poolname]['_urns'].items():
                            pool, ptype, sn = parseUrn(urn)
                            self._dTypes, self._dTags, sn = \
                                populate_pool2(tags, ptype, sn, self._dTypes,
                                               self._dTags)
                        logger.debug(
                            f'HK updated for the pool {self.poolname}.')
                else:
                    logger.info(f'No pool found by the name {self.poolname}')
            else:
                logger.info(f'No pool found.')
            return rdata
        else:
            raise ValueError(res['msg'])

    def exists(self, urn):
        """
        Determines the existence of a product with specified URN.
        """
        res = read_from_cloud('infoUrn', urn=urn, token=self.token)
        if res['code'] == 0:
            return True
        else:
            return False

    def getProductClasses(self):
        """
        Returns all Product classes found in this pool.
        mh: returns an iterator.
        """
        classes = []
        try:
            if self.poolInfo is None:
                self.getPoolInfo()
                if self.poolInfo is None:
                    # No such pool in cloud
                    return None
            classes = list(self.poolInfo[self.poolname]['_classes'])
            return classes
        except TypeError as e:
            raise TypeError(
                f'Pool info API changed or unexpected information: {e} trbk: {trbk(e)}')

    def getCount(self, typename=None):
        """
        Return the number of URNs for the product type.
        """

        clzes = self.getProductClasses()
        if clzes == 0:
            return 0
        _c = self.poolInfo[self.poolname]['_classes']
        if typename is None:
            return sum(len(td['sn']) for td in _c.values())
        if typename not in clzes:
            # raise ValueError("Current pool has no such type: " + typename)
            return 0
        return len(_c[typename]['sn'])

    def isEmpty(self):
        """
        Determines if the pool is empty.
        """
        res = self.getPoolInfo()
        if issubclass(res.__class__, dict):
            clses = res[self.poolname]['_classes']
            return len(clses) == 0
        else:
            raise ValueError('Error getting PoolInfo ' + str(res))

    def getMetaByUrn(self, urn=None, resourcetype=None, index=None):
        """
        Get all of the meta data belonging to a product of a given URN.

        mh: returns an iterator.
        """
        res = read_from_cloud(requestName='getMeta', urn=urn, token=self.token)
        return res

    def meta(self, *args, **kwds):
        """        Loads the meta-data info belonging to the product of specified URN.
        """
        return self.getMetaByUrn(*args, **kwds)

    def getDataType(self, urn=None):
        """Returns the Datatype of one or a list of URNs.

        Parameters
        ----------
        urn : str, list, None

        Returns
        -------
        dict, list
            all types if `urn` is not given. one or a list of
            datatypes (None if the URN is not found, '' of no
            Datatype.

        Examples
        --------
        FIXME: Add docs.

        """

        if urn is None:
            res = read_from_cloud('getDataType', token=self.token)
            return res
        return self.get_DataInfo(urn, 'productType')

    def getDataInfo(self, what='', paths=None, pool=None, limit=10000, asyn=False):
        """Returns the CSDB storage information of one or a list of URNs.

        Parameters
        ----------
        what : str
            which item in ['data'] list to return. e.g. 'urn' means 
            a list
            of URNs found in the path. Default '' for all items.
        paths : str, list, None
            part in a path. Typical uses: '{poolname}' for a pool, 
            or '/{poolname}/{product-type}' for a type of products in a pool,
            or '{poolname}/{product-name}/{index.aka.serial-number}',
            e.g. '/sv1/sv.BaseProduct' for all 'sv.BasePRoduct' products in pool 'sv1'.
            Only one  of `paths` and `pool` can be non-empty.
            default is `None`.
        pool : str, None
            Only one  of `paths` and `pool` can be non-empty.
            Default is `None` for `self` pool if `paths` is empty,
            empty if `paths` is not.
        limit : int
            Maximum record number. Default `None` for 10000.

        Returns
        -------
        dict, list
            `None` if `paths` and `pool` are not found. one or a list of
            value for the given `what` key (None if not found).

        Examples
        --------
        FIXME: Add docs.

        """
        pname = self._poolname
        listpa = isinstance(paths, (list, tuple))
        if not listpa:
            paths = [paths]
        pa = []
        for a in paths:
            if a and pool:
                raise ValueError(
                    f"Path '{a}' and pool '{pool}' cannot be both non-empty for getDataInfo.")
            # if both are empty, pool takes self.poolname
            pa.append(a)
        if not pool:
            pool = pname
        if listpa:
            res = read_from_cloud('getDataInfo', token=self.token,
                                  paths=pa, pool=pool, limit=limit, asyn=asyn)
            # if input is list the output each query is a list
            if what:
                return [get_Values_From_A_list_of_dicts(r, what) for r in res]
            else:
                return res
        else:
            res = read_from_cloud('getDataInfo', token=self.token,
                                  paths=pa[0], pool=pool, limit=limit)
            # if input is not list the output of each query is not a list
            if what:
                return get_Values_From_A_list_of_dicts(res, what)
            else:
                return res if len(res) > 1 else res[0] if res else None

    def doSave(self, resourcetype, index, data, tag=None, serialize_in=True, **kwds):
        path = '/' + self._poolname + '/' + resourcetype
        res = load_from_cloud('uploadProduct', token=self.token,
                              products=data, path=path, tags=tag, resourcetype=resourcetype, **kwds)
        return res

    def saveOne(self, prd, tag, geturnobjs, serialize_in, serialize_out, res, check_type=True, **kwds):
        """
                Save one product.

                :res: list of result.
                :serialize_out: if True returns contents in serialized form.
                """

        jsonPrd = prd
        if serialize_in:
            pn = fullname(prd)
            cls = prd.__class__
            jsonPrd = serialize(prd)
        else:
            # prd is json. extract prod name
            # '... "_STID": "Product"}]'
            pn = prd.rsplit('"', 2)[1]
            cls = Class_Look_Up[pn]
            pn = fullname(cls)

        if check_type:
            datatype = self.getDataType()
            if pn not in datatype:
                raise ValueError('No such product type in cloud: ' + pn)

        # targetPoolpath = self.getPoolpath() + '/' + pn
        try:
            # save prod to cloud
            if serialize_in:
                uploadRes = self.doSave(resourcetype=pn,
                                        index=None,
                                        data=jsonPrd,
                                        tag=tag,
                                        serialize_in=serialize_in,
                                        serialize_out=serialize_out,
                                        **kwds)

            else:
                uploadRes = self.doSave(resourcetype=pn,
                                        index=None,
                                        data=prd,
                                        tag=tag,
                                        serialize_in=serialize_in,
                                        serialize_out=serialize_out,
                                        **kwds)
        except ValueError as e:
            msg = f'product {self.poolname}/{pn} saving failed. {e} {trbk(e)}'
            logger.debug(msg)
            raise e

        if uploadRes['msg'] != 'success':
            raise Exception('Upload failed: product "%s" to %s:' % (
                prd.description, self.poolurl) + uploadRes['msg'])
        else:
            urn = uploadRes['data']['urn']

        if geturnobjs:
            if serialize_out:
                # return the URN string.
                res.append(urn)
            else:
                res.append(Urn(urn))
        else:
            rf = ProductRef(urn=Urn(urn, poolurl=self.poolurl))
            if serialize_out:
                # return without meta
                res.append(rf)
            else:
                # it seems that there is no better way to set meta
                rf._meta = prd.getMeta()
                res.append(rf)

    def schematicSave(self, products, tag=None, geturnobjs=False, serialize_in=True, serialize_out=False, asyn=False, **kwds):
        """ do the scheme-specific saving.

            :serialize_out: if True returns contents in serialized form.
        """
        res = []
        if not PoolManager.isLoaded(self._poolname):  # self.poolExists():
            raise ValueError(f'Pool {self._poolname} is not registered.')
        if serialize_in:
            alist = issubclass(products.__class__, list)
            if not alist:
                prd = products
                self.saveOne(prd, tag, geturnobjs,
                             serialize_in, serialize_out, res, kwds)
            else:
                for prd in products:
                    self.saveOne(prd, tag, geturnobjs,
                                 serialize_in, serialize_out, res, kwds)
        else:
            alist = products.lstrip().startswith('[')
            if not alist:
                prd = products
                self.saveOne(prd, tag, geturnobjs,
                             serialize_in, serialize_out, res, kwds)
            else:
                # parse '[ size1, prd, size2, prd2, ...]'

                last_end = 1
                productlist = []
                comma = products.find(',', last_end)
                while comma > 0:
                    length = int(products[last_end: comma])
                    productlist.append(length)
                    last_end = comma + 1 + length
                    prd = products[comma + 2: last_end + 1]
                    self.saveOne(prd, tag, geturnobjs,
                                 serialize_in, serialize_out, res, kwds)
                    # +2 to skip the following ', '
                    last_end += 2
                    comma = products.find(',', last_end)
        # XXX refresh currentSn on server
        self.getPoolInfo()
        sz = 1 if not alist else len(
            products) if serialize_in else len(productlist)
        logger.debug('%d product(s) generated %d %s: %s.' %
                     (sz, len(res), 'Urns ' if geturnobjs else 'prodRefs', lls(res, 200)))

        if alist:
            return serialize(res) if serialize_out else res
        else:
            return serialize(res[0]) if serialize_out else res[0]

    def schematicLoad(self, resourcetype, index, start=None, end=None,
                      serialize_out=False):
        """ do the scheme-specific loading
        """

        spn = self._poolname
        poolInfo = self.getPoolInfo()
        try:
            if poolInfo['data']:
                pinfo = poolInfo['data']
                if spn in pinfo:
                    if index in pinfo[spn]['_classes'][resourcetype]['sn']:
                        urn = makeUrn(poolname=spn,
                                      typename=resourcetype, index=index)
                        res = load_from_cloud(
                            'pullProduct', token=self.token, urn=urn)
                        # res is a product like fdi.dataset.product.Product

                        if issubclass(res.__class__, BaseProduct):
                            if serialize_out:
                                from fdi.dataset.deserialize import serialize
                                return serialize(res)
                            else:
                                return res
                        else:
                            raise Exception('Load failed: ' + res['msg'])
        except Exception as e:
            logger.debug('Load product failed:' + str(e))
            __import__("pdb").set_trace()

            raise e
        logger.debug('No such product:' + resourcetype +
                     ' with index: ' + str(index))
        raise ValueError('No such product:' + resourcetype +
                         ' with index: ' + str(index))

    def doLoad(self, resourcetype, index, start=None, end=None, serialize_out=False):
        """ to be implemented by subclasses to do the action of loading
        """
        raise NotImplementedError

    # def schematicRemove(self, urn=None, resourcetype=None, index=None, asyn=False, **kwds):
    #     """ do the scheme-specific removing.

    #     `resourcetype+index` takes priority over `urn`.
    #     """
    #     prod, sn, urn = self.get_missing(urn, resourcetype, index,
    #                                      no_check=True)
    #     if index is None or index == '':
    #         self.schematicWipe()
    #         return

    #     if issubclass(index.__class__, (list, tuple)):
    #         if asyn:
    #             return
    #         else:
    #             for i, ind in enumerate(index):
    #                 self.doRemove(resourcetype, ind)
    #     else:
    #         # a single product
    #         return self.doRemove(resourcetype, index)

    def doRemove(self, resourcetype, index):
        """ to be implemented by subclasses to do the action of reemoving
        """
        # path = self._cloudpoolpath + '/' + resourcetype + '/' + str(index)
        path0 = f'/{self._poolname}/{resourcetype}'
        path = f'{path0}/{index}'
        res = read_from_cloud('remove', token=self.token, path=path)
        if res['code']:
            msg = f"Remove product_meta {path} failed: {res['msg']}"
            raise ValueError(msg)

        return res

    def doAsyncRemove(self, resourcetype, index):
        """ implemented with aio to do the action of removing asynchronously.
        """
        # path = self._cloudpoolpath + '/' + resourcetype + '/' + str(index)

        res = read_from_cloud('remove', token=self.token, path=path)
        if res['code'] and not getattr(self, 'ignore_error_when_delete', False):
            raise ValueError(
                f"Remove product_meta {path} failed: {res['msg']}")
        logger.debug(f"Remove {path} code: {res['code']} {res['msg']}")

        return res

#     def schematicWipe(self, restore_type=True):
#
#         self.doWipe(restore_type)

    def doWipe(self, restore_type=False):
        """ to be implemented by subclasses to do the action of wiping.
        """
        poolname = self._poolname

        # res = read_from_cloud(
        #     'wipePool', poolname=poolname, token=self.token)
        # if res['msg'] != 'success':
        #     raise ValueError('Wipe pool ' + poolname +
        #                      ' failed: ' + res['msg'])
        # return
        info = self.getPoolInfo()
        path = None
        if isinstance(info, dict):
            for clazz, cld in info[poolname]['_classes'].items():
                path = f'/{poolname}/{clazz}'

                if clazz == 'fdi.dataset.testproducts.TP':
                    # csdb bug, remove all one-by-one
                    for s in cld['sn']:
                        if s == 426:
                            continue
                        res = self.doRemove(resourcetype=clazz, index=s)
                else:
                    # can use delDataType
                    res = read_from_cloud(
                        'delDataType', path=path, token=self.token)
                if res['msg'] != 'success':
                    msg = f'Wipe pool {poolname} failed: ' + res['msg']
                    if getattr(self, 'ignore_error_when_delete', False):
                        logger.warning(msg)
                    else:
                        raise ValueError(msg)

            if restore_type:
                # restore deleted datatype by error by csdb
                res = read_from_cloud(
                    'uploadDataType', cls_full_name=clazz, token=self.token)
                if res['code'] != 0:
                    msg = f'Restoring Datatype {clazz} when wiping pool {poolname} failed: ' + \
                        res['msg']
                    if getattr(self, 'ignore_error_when_delete', False):
                        logger.warning(msg)
                    else:
                        raise ValueError(msg)
            logger.debug(f'Done removing {path}')
        else:
            raise ValueError("Update pool information failed: " + str(info))

    def setTag(self, tag, urn):
        """ Set given tag or list of tags to the URN.

        Parameters
        ----------
        :tag: tag or list of tags.
        """
        u = urn.urn if issubclass(urn.__class__, Urn) else urn
        if not self.exists(urn):
            raise ValueError('Urn does not exists!')
        if isinstance(tag, (list, str)) and len(tag) > 0:
            t = ', '.join(tag) if isinstance(tag, list) else tag
            res = read_from_cloud(
                'addTag', token=self.token, tags=t, urn=u)
            if res['msg'] != 'OK':
                raise ValueError('Set tag to ' + urn +
                                 ' failed: ' + res['msg'])
        else:
            raise ValueError('Tag can not be empty or non-string!')

    def getTags(self, urn=None):
        u = urn.urn if issubclass(urn.__class__, Urn) else urn
        res = read_from_cloud('infoUrn', urn=u, token=self.token)
        if res['code'] == 0:
            ts = [t.split(',') for t in res['data'][u]['tags']]
            return [x.strip() for x in chain(*ts)]
        else:
            raise ValueError('Read tags failed due to : ' + res['msg'])

    def removeTagByUrn(self, tag, urn):
        pass

    def removeTag(self, tag):
        if isinstance(tag, str):
            res = delete_from_server('delTag', token=self.token, tag=tag)
        else:
            raise ValueError('Tag must be a string!')

    def meta_filter(self, q, typename=None, reflist=None, urnlist=None, snlist=None):
        """ returns filtered collection using the query.

        q is a MetaQuery
        valid inputs: typename and ns list; productref list; urn list
        """
        pass

    def prod_filter(self, q, cls=None, reflist=None, urnlist=None, snlist=None):
        """ returns filtered collection using the query.

        q: an AbstractQuery.
        valid inputs: cls and ns list; productref list; urn list
        """

    def doSelect(self, query, results=None):
        """
        to be implemented by subclasses to do the action of querying.
        """
        raise (NotImplementedError)


# =================SAVE REMOVE LOAD================
# test_getToken2()
# test_poolInfo()
# test_upload()
# test_get()
# test_remove()
# test_multi_upload()
# prd = genProduct(1)
# res = cp.schematicSave(prd)
# cp.schematicRemove('urn:poolbs:20211018:4')

# cp.schematicLoad('fdi.dataset.product.Product', 1)
# cp.schematicLoad('20211018', 5)
