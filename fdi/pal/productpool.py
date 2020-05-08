# -*- coding: utf-8 -*-
from ..dataset.odict import ODict
from .urn import Urn, parseUrn
from .versionable import Versionable
from .taggable import Taggable
from .definable import Definable
from ..utils.common import pathjoin
from .productref import ProductRef
import logging
import filelock
from copy import deepcopy
import os
import sys

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
    from urllib.parse import urlparse
else:
    PY3 = False
    from urlparse import urlparse

# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))


lockpathbase = '/tmp/locks'


class ProductPool(Definable, Taggable, Versionable):
    """ A mechanism that can store and retrieve Products.

A product pool should not be used directly by users. The general user should access data in a ProductPool through a ProductStorage instance.

When implementing a ProductPool, the following rules need to be applied:

    1. Pools must guarantee that a Product saved via the pool saveProduct(Product) method is stored persistently, and that method returns a unique identifier (URN). If it is not possible to save a Product, an IOException shall be raised.
    2. A saved Product can be retrieved using the loadProduct(Urn) method, using as the argument the same URN that assigned to that Product in the earlier saveProduct(Product) call. No other Product shall be retrievable by that same URN. If this is not possible, an IOException or GeneralSecurityException is raised.
    3. Pools should not implement functionality currently implemented in the core paclage. Specifically, it should not address functionality provided in the Context abstract class, and it should not implement versioning/cloning support.

    """

    def __init__(self, poolurn='file:///tmp/pool', **kwds):
        # print(__name__ + str(kwds))
        super(ProductPool, self).__init__(**kwds)
        self._poolurn = poolurn
        pr = urlparse(poolurn)
        self._scheme = pr.scheme
        self._place = pr.netloc
        # convenient access path
        self._poolpath = pr.netloc + \
            pr.path if pr.scheme in ('file') else pr.path
        # {type|classname -> {'sn:[sn]'}}
        self._classes = ODict()
        logger.debug(self._poolpath)

    def lockpath(self):
        lp = pathjoin(lockpathbase, self._poolpath)
        if not os.path.exists(lp):
            os.makedirs(lp)
        lf = pathjoin(lp, 'lock')
        return lf

    def accept(self, visitor):
        """ Hook for adding functionality to object
        through visitor pattern."""
        visitor.visit(self)

    def dereference(self, ref):
        """
        Decrement the reference count of a ProductRef.
        """
        self._urns[ref.urn]['refcnt'] -= 1

    def exists(self, urn):
        """
        Determines the existence of a product with specified URN.
        """
        return urn in self._urns

    def getDefinition(self):
        """
        Returns pool definition info which contains pool type and other pool specific configuration parameters
        """
        return super(ProductPool, self).getDefinition()

    def getId(self):
        """
        Gets the identifier of this pool.
        """
        return self._poolurn

    def getProductClasses(self):
        """
        Returns all Product classes found in this pool.
        mh: returns an iterator.
        """
        return self._classes.keys()

    def getReferenceCount(self, ref):
        """
        Returns the reference count of a ProductRef.
        """
        self._urns[ref.urn]['refcnt'] += 1

    def getUrnId(self):
        """
        Get the identifier of this pool used to build URN, usually it's same as id returned by getId().
        """
        return self.getId()

    def isAlive(self):
        """
        Test if the pool is capable of responding to commands.
        """
        return True

    def isEmpty(self):
        """
        Determines if the pool is empty.
        """
        return len(self._urns) == 0

    def loadDescriptors(self, urn):
        """
        Loads the descriptors belonging to specified URN.
        """
        return self._urns[urn]

    def schematicLoadProduct(self, resourcename, indexstr):
        """ to be implemented by subclasses to do the scheme-specific loading
        """
        raise(NotImplementedError)

    def loadProduct(self, urn):
        """
        Loads a Product belonging to specified URN.
        """
        poolname, resourcecn, indexs, scheme, place, poolpath = parseUrn(urn)
        if poolname != self._poolurn:
            raise(ValueError('wrong pool: ' + poolname +
                             ' . This is ' + self._poolurn))

        return self.schematicLoadProduct(resourcecn, indexs)

    def meta(self,  urn):
        """
        Loads the meta-data belonging to the product of specified URN.
        """
        return self._urns[urn]['meta']

    def reference(self,  ref):
        """
        Increment the reference count of a ProductRef.
        """

    def schematicRemove(self,  typename, serialnum):
        """ to be implemented by subclasses to do the scheme-specific removing
        """
        raise(NotImplementedError)

    def remove(self,  urn):
        """
        Removes a Product belonging to specified URN.
        """

        poolname, resourcecn, indexs, scheme, place, poolpath = parseUrn(urn)

        if self._poolurn != poolname:
            raise ValueError(
                urn + ' is not from the pool ' + pool)

        prod = resourcecn
        sn = int(indexs)

        c, t, u = self._classes, self._tags, self._urns
        # save a copy for rolling back
        cs, ts, us = deepcopy(c), deepcopy(t), deepcopy(u)

        if urn not in u:
            raise ValueError(
                '%s not found in pool %s.' % (urn, self.getId()))

        with filelock.FileLock(self.lockpath()):
            self.removeUrn(urn)
            c[prod]['sn'].remove(sn)
            if len(c[prod]['sn']) == 0:
                del c[prod]
            try:
                self.schematicRemove(typename=prod,
                                     serialnum=sn)
            except Exception as e:
                msg = 'product ' + urn + ' removal failed'
                logger.debug(msg)
                # undo changes
                c, t, u = cs, ts, us
                raise e

    def removeAll(self):
        """
        Remove all pool data (self, products) and all pool meta data (self, descriptors, indices, etc.).
        """

        try:
            self.schematicWipe()
        except Exception as e:
            msg = self.getId() + 'wiping failed'
            logger.debug(msg)
            raise e
        self._classes.clear()
        self._tags.clear()
        self._urns.clear()
        logger.debug('Done.')

    def saveDescriptors(self,  urn,  desc):
        """
        Save/Update descriptors in pool.
        """

    def schematicSave(self,  typename, serialnum, data):
        """ to be implemented by subclasses to do the scheme-specific saving
        """
        raise(NotImplementedError)

    def saveProduct(self,  product, tag=None, geturnobjs=False):
        """
        Saves specified product and returns the designated ProductRefs or URNs.
        Saves a product or a list of products to the pool, possibly under the
        supplied tag, and return the reference (or a list of references is
        the input is a list of products), or Urns if geturnobjs is True.

        Pool:!!dict
          _classes:!!odict
              $product0_class_name:!!dict
                      currentSN:!!int $the serial number of the latest added prod to the pool
                             sn:!!list
                                 - $serial number of a prod  
                                 - $serial number of a prod  
                                 - ...
              $product0_class_name:!!dict
              ...
          _urns:!!odict
              $URN0:!!odict
                      meta:!!MetaData $prod.meta
                      tags:!!list
                            - $tag
                            - $tag
                            - ...
          _tags:!!odict
              urns:!!list
                   - $urn
                   - $urn
                   - ...
          $urn:!!$serialized product
        """
        c, t, u = self._classes, self._tags, self._urns
        # save a copy
        cs, ts, us = deepcopy(c), deepcopy(t), deepcopy(u)

        if not issubclass(product.__class__, list):
            prds = [product]
        else:
            prds = product
        res = []
        for prd in prds:
            pn = prd.__class__.__name__
            with filelock.FileLock(self.lockpath()):
                if pn in c:
                    sn = (c[pn]['currentSN'] + 1)
                else:
                    sn = 0
                    c[pn] = ODict(sn=[])

                c[pn]['currentSN'] = sn
                c[pn]['sn'].append(sn)
                urnobj = Urn(cls=prd.__class__, pool=self._poolurn, index=sn)
                urn = urnobj.urn

                if urn not in u:
                    u[urn] = ODict(tags=[], meta=prd.meta)

                if tag is not None:
                    self.setTag(tag, urn)

                try:
                    self.schematicSave(typename=pn,
                                       serialnum=sn,
                                       data=prd)
                except Exception as e:
                    msg = 'product ' + urn + ' saving failed'
                    logger.debug(msg)
                    # undo changes
                    c, t, u = cs, ts, us
                    raise e
            if geturnobjs:
                res.append(urnobj)
            else:
                rf = ProductRef(urn=urnobj)
                # it seems that there is no better way to set meta
                rf._meta = prd.getMeta()
                rf._poolurn = self._poolurn
                res.append(rf)
        logger.debug('generated ' + 'Urns ' if geturnobjs else 'prodRefs ' +
                     str(len(res)))
        if issubclass(product.__class__, list):
            return res
        else:
            return res[0]

    def select(self,  query):
        """
        Returns a list of references to products that match the specified query.
        """
        c, t, u = self._classes, self._tags, self._urns
        cs, ts, us = deepcopy(c), deepcopy(t), deepcopy(u)
        return

    def select(self,  query,  results):
        """
        Refines a previous query, given the refined query and result of the previous query.
        """
        return

    def __repr__(self):
        return self.__class__.__name__ + ' { pool= ' + str(self._poolurn) + ' }'