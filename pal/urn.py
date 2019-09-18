# -*- coding: utf-8 -*-
import os

import logging
# create logger
logger = logging.getLogger(__name__)
#logger.debug('level %d' %  (logger.getEffectiveLevel()))

from pathlib import Path
from urllib.parse import urlparse

from dataset.eq import DeepEqual
from dataset.odict import ODict
from dataset.serializable import Serializable

from .comparable import Comparable
#from .common import getClass


def parseUrn(urn):
    """
    Checks the URN string is valid in its form and splits it. For example if the urn is ``urn:file://c:/tmp/mypool/proj1.product:322`` into poolname ``file://c:/tmp/mypool/proj1.product:322`` into poolname ``file://c:/tmp/mypool``, resource type (usually class) name ``proj1.product``, serial number in string ``'322'``, scheme ``file``, place ``c:`` (with ip and port if given), and poolpath ``c:/tmp/mypool``
    """
    if not issubclass(urn.__class__, str):
        raise TypeError('a urn string needed')
    # is a urn?
    sp1 = urn.split(':', maxsplit=1)
    if sp1[0] != 'urn':
        raise ValueError('a urn string must start with \'urn\'')
    if len(sp1) < 2:
        raise ValueError('bad urn: ' + sp1[1])
    # maxsplit=2 so that if netloc is e.g. c: or http: , the : in it is not parsed:
    sp2 = sp1[1].rsplit(':', maxsplit=2)
    if len(sp2) < 3:
        raise ValueError('bad urn: ' + sp1[1])
    serialnumstr = sp2[2]
    resourceclass = sp2[1]
    poolname = sp2[0]
    pr = urlparse(poolname)
    scheme = pr.scheme
    place = pr.netloc
    # convenient access path
    poolpath = place + pr.path if scheme in ('file', 'mem') else pr.path
    return poolname, resourceclass, serialnumstr, scheme, place, poolpath


def makeUrn(poolname, typename, index):
    """ assembles a URN with infos of the pool, the resource type, and the index
    """
    return 'urn:' + poolname + ':' + typename + ':' + str(index)


class Urn(DeepEqual, Serializable, Comparable):
    """ The object representation of the product URN string. The 
    memory consumed by sets of this object are much less than sets
    of URN strings.

    Only when the class types in URN string are not in classpath, 
    the urn object will consume equals or a little more than URN string 
    as the object has to hold the original urn string. However this should
    be considered as exceptional cases.

    Using this object representation also help to avoid parsing cost of
    URN string.
    mh: URN format: 'urn:poolname:resourceclass:serialnumber'
    resourceclass: dataset.Product ... etc
    poolname format: scheme + '://' + place + directory
    scheme format: file, ram, http ... etc
    place format: 192.168.5.6:8080, c: ... etc
    directory format: 
    for 'file' scheme: '/' + name + '/' + name + ... + '/' + name
    for 'mem' scheme: '/' + name + '/' + name + ... + '/' + process_ID
    serialnumber format: str(int). 
    for file scheme : internal index; 
    for memm scheme: python object id
    """

    def __init__(self, urn=None, pool=None, cls=None, index=None, **kwds):
        """
        Creates the URN object with the urn string or components.
        if urn is given and pool, class, etc are also specified,
        the latter are ignored. else the URN is constructed from them.
        Urn(u) will make a Urn object out of u.
        """
        super().__init__(**kwds)

        if urn is None:
            if cls is None or pool is None or index is None:
                if cls is None and pool is None and index is None:
                    self._scheme = None
                    self._place = None
                    self._pool = None
                    self._class = None
                    self._index = None
                    self._resource = None
                    self._poolpath = None
                    self._urn = None
                    return
                else:
                    raise ValueError('give urn or all other arguments')
            urn = makeUrn(poolname=pool,
                          typename=cls.__qualname__,
                          index=index)
        self.setUrn(urn)

    @staticmethod
    def getInMemUrnObj(x):
        ps = 'mem:///' + str(os.getpid())
        return Urn(cls=x.__class__, pool=ps, index=id(x))

    @property
    def urn(self):
        """ property
        """
        return self.getUrn()

    @urn.setter
    def urn(self, urn):
        """ property
        """
        self.setUrn(urn)

    def setUrn(self, urn):
        """ parse urn to get scheme, place, pool, resource, index.
        """

        poolname, resourcecn, indexs, scheme, place, poolpath = \
            parseUrn(urn)

        cls = resourcecn  # getClass(resourcecn)

        self._scheme = scheme
        self._place = place
        self._pool = poolname
        self._class = cls
        self._index = int(indexs)
        self._resource = resourcecn + ':' + indexs
        self._poolpath = poolpath
        self._urn = urn
        # logger.debug(urn)

    def getUrn(self):
        """ Returns the urn in this """
        return self._urn

    def getType1(self):
        """ Returns class type of Urn
        """
        return self._class

    def getTypeName(self):
        """ Returns class type name of Urn.
        """
        return self._class  # .__qualname__

    def getIndex(self):
        """ Returns the product index.
        """
        return self._index

    def getScheme(self):
        """ Returns the urn scheme.
        """
        return self._scheme

    def getUrnWithoutPoolId(self):
        return self._resource

    @property
    def place(self):
        return self.getPlace()

    def getPlace(self):
        """ Returns the netloc in this """
        return self._place

    @staticmethod
    def getFullPath(urn):
        """ returns the place+poolname+resource directory of the urn
        """
        poolname, resourcecn, indexs, scheme, place, poolpath = parseUrn(
            urn)
        return poolpath + '/' + resourcecn + '_' + indexs

    @property
    def pool(self):
        """ returns the pool URN.
        """
        return self.getPoolId()

    def getPoolId(self):
        """ Returns the pool URN in this """
        return self._pool

    def getPool(self):
        """ Returns the pool name in this """
        return self.getPoolId()

    def hasData(self):
        """ Returns whether this data wrapper has data. """
        return len(self.getData()) > 0

    def __eq__(self, o):
        """
        mh: compare urn only
        """

        return self.getUrn() == o.getUrn()

    def serializable(self):
        """ Can be encoded with serializableEncoder """
        return ODict(urn=self.urn,
                     classID=self.classID,
                     version=self.version)

    def __repr__(self):
        return self.__class__.__name__ + ' ' + self._urn

    def toString(self):
        return self.__class__.__name__ + \
            '{ %s, scheme:%s, place:%s, pool:%s, type:%s, index:%d, poolpath: %s}' % (
                self._urn,
                self._scheme,
                self._place,
                self._pool,
                self._class,  # .__qualname__,
                self._index,
                self._poolpath
            )