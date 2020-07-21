# -*- coding: utf-8 -*-

from .context import Context
from .urn import Urn
from .comparable import Comparable
from ..dataset.product import Product
from ..dataset.odict import ODict
from ..dataset.serializable import Serializable
from ..dataset.metadataholder import MetaDataHolder
import logging
# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))


class ProductRef(MetaDataHolder, Serializable, Comparable):
    """ A lightweight reference to a product that is stored in a ProductPool or in memory.
    """

    def __init__(self, urn=None, poolurn=None, product=None, meta=None, **kwds):
        """ Urn can be the string or URNobject. if product is provided create an in-memory URN.
        Poolurn if given overrides the pool URN in urn, and causes metadata to be loaded from pool, unloss this prodref points to a mempool.
        If meta is given, it will be used instead of that from poolurn.
        A productref created from a single product will result in a memory pool urn, and the metadata won't be loaded.
        """
        super(ProductRef, self).__init__(**kwds)
        if issubclass(urn.__class__, str):
            urnobj = Urn(urn)
        elif issubclass(urn.__class__, Urn):
            urnobj = urn
        elif issubclass(urn.__class__, Product):
            # allow ProductRef(p) where p is a Product
            if product is None:
                product = urn
        else:
            urnobj = None

        if product:
            from .poolmanager import PoolManager, DEFAULT_MEM_POOL
            from . import productstorage
            poolurn = DEFAULT_MEM_POOL
            pool = PoolManager.getPool(poolurn)
            st = productstorage.ProductStorage(pool)
            urnobj = st.save(product, geturnobjs=True)
            # a lone product passed to prodref will be stored to mempool

        self.setUrnObj(urnobj, poolurn, meta)

        if product and isinstance(product, Context):
            self._product = product

        self._parents = []

    @property
    def product(self):
        return self.getProduct()

    def getProduct(self):
        """ Get the product that this reference points to.

        If the product is a Context, it is kept internally, so further accesses don't need to ask the storage for loading it again.
        Otherwise, the product is returned but the internal reference remains null, so every call to this method involves a request to the storage.

        This way, heavy products are not kept in memory after calling this method, thus maintaining the ProductRef a lighweight reference to the target product.

        In case of a Context, if it is wanted to free the reference, call unload().

        Returns:
        the product
        """

        if self._storage is None:
            return None
        if hasattr(self, '_product') and self._product is not None:
            return self._product
        from .poolmanager import PoolManager
        p = PoolManager.getPool(self._poolurn).loadProduct(self.getUrn())
        if issubclass(p.__class__, Context):
            self._product = p
        return p

    def getStorage(self):
        """ Returns the product storage associated.
        """
        return self._storage

    def setStorage(self, storage):
        """ Sets the product storage associated.
        """
        self._storage = storage
        # if hasattr(self, '_urn') and self._urn:
        #    self._meta = self._storage.getMeta(self._urn)

    def getType(self):
        """ Specifies the Product class to which this Product reference is pointing to.
        """
        return self._urnobj.getType()

    @property
    def urn(self):
        """ Property """
        return self.getUrn()

    @urn.setter
    def urn(self, urn):
        """
        """
        self.setUrn(urn)

    def setUrn(self, urn):
        """
        """
        self.setUrnObj(Urn(urn))

    def getUrn(self):
        """ Returns the Uniform Resource Name (URN) of the product.
        """
        return self._urnobj.urn

    @property
    def urnobj(self):
        """ Property """
        return self.getUrnObj()

    @urnobj.setter
    def urnobj(self, urnobj):
        """
        """
        self.setUrnObj(urnobj)

    def setUrnObj(self, urnobj, poolurn=None, meta=None):
        """ sets urn
        Poolurn if given overrides the pool URN in urn, and causes metadata to be loaded from pool.
        A productref created from a single product will result in a memory pool urn, and the metadata won't be loaded.
        If meta is given, it will be used instead of that from poolurn.
        """
        if urnobj is not None:
            # logger.debug(urnobj)
            assert issubclass(urnobj.__class__, Urn)

        self._urnobj = urnobj
        if urnobj is not None:
            self._urn = urnobj.urn
            # if hasattr(self, '_storage') and self._storage:
            #    self._meta = self._storage.getMeta(self._urn)

            from .poolmanager import PoolManager, DEFAULT_MEM_POOL
            from . import productstorage
            loadmeta = (poolurn or meta) and poolurn != DEFAULT_MEM_POOL
            if poolurn is None:
                poolurn = urnobj.pool
            pool = PoolManager.getPool(poolurn)
            self._meta = (meta if meta else pool.meta(
                urnobj.urn)) if loadmeta else None
            st = productstorage.ProductStorage(pool)
            self._storage = st
            self._poolurn = poolurn
            self._product = None
        else:
            self._urn = None
            self._storage = None
            self._poolurn = None
            self._meta = None
            self._product = None

    def getUrnObj(self):
        """ Returns the URN as an object.
        """
        return self._urnobj

    @property
    def meta(self):
        """ Property """
        return self.getMeta()

    def getMeta(self):
        """ Returns the metadata of the product.
        """
        return self._meta

    def getHash(self):
        """ Returns a code number for the product; actually its MD5 signature.
        This allows checking whether a product already exists in a pool or not.
        """
        raise NotImplementedError()

    def getSize(self):
        """ Returns the estimated size(in bytes) of the product in memory.
        Useful for providing this information for a user that wants to download the product from a remote site.
        Returns:
        the size in bytes
        """
        raise NotImplementedError()

    def unload(self):
        """ Clear the cached meta and frees internal reference to the product, so it can be garbage collected.
        """
        self._product = None
        self._meta = None

    def isLoaded(self):
        """ Informs whether the pointed product is already loaded.
        """
        return self._product is not None

    def addParent(self, parent):
        """ add a parent
        """
        self._parents.append(parent)

    def removeParent(self, parent):
        """ remove a parent
        """
        self._parents.remove(parent)

    @property
    def parents(self):
        """ property """

        return self.getParents()

    @parents.setter
    def parents(self, parents):
        """ property """

        self.setParents(parents)

    def getParents(self):
        """ Return the in-memory parent context products of this reference.
        That is, the contexts in program memory that contain this product reference object.
        A context that contains a different product reference object pointing to the same URN is not a parent of this product reference.

        Furthermore, it should be understood that this method does not return the parent contexts of the product pointed to by this reference as stored in any underlying pool or storage.

        Returns:
        the parents
        """
        return self._parents

    def setParents(self, parents):
        """ Sets the in-memory parent context products of this reference.
        """
        self._parents = parents

    def equals(self, o):
        """     true if o is a non-null ProductRef, with the same Product type than this one, and:

        urns and products are null in both refs, or
        nurs are equal and products are null, or # <-- mh
        urns are null in both refs, and their products are equal, or
        urns and products are equal in both refs
        """
        t1 = issubclass(o.__class__, ProductRef)
        if not t1:
            return False
        if self._product is None:
            if o._product is None:
                if o._urnobj is None and self._urnobj is None or o._urnobj == self._urnobj:
                    return True
            else:
                return False
        else:
            if self._product == o._product and (self._product.type == o._product.type):
                if (o._urnobj is None and self._urnobj is None) or \
                   (o._urnobj == self._urnobj):
                    return True

        return False

    def __eq__(self, o):
        """ has the same Urn.
        """
        return self.equals(o)

    def __hash__(self):
        """ returns hash of the URN object
        """
        return hash(self._urnobj)

    def __repr__(self):
        return self.__class__.__name__ + '{ ProductURN=' + self.urn + ', meta=' + str(self.getMeta()) + '}'

    def toString(self, matprint=None, trans=True):
        """
        """
        s = '# ' + self.__class__.__name__ + '\n'
        s += '# ' + self.urn + '\n'
        s += '# Parents:' + \
            str([p.__class__.__name__ +
                 '(' + p.description + ')'
                 for p in self.parents]) + '\n'
        s += '# meta;' + self.meta.toString()
        return s

    def serializable(self):
        """ Can be encoded with serializableEncoder """
        return ODict(urnobj=self.urnobj if issubclass(self.urnobj.__class__, Urn) else None,
                     _meta=self.getMeta(),
                     classID=self.classID,
                     version=self.version)
