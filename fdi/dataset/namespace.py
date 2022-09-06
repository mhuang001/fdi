# -*- coding: utf-8 -*-


from collections import ChainMap
import sys
import logging
import copy
from functools import lru_cache

if sys.version_info[0] >= 3:  # + 0.1 * sys.version_info[1] >= 3.3:
    PY3 = True
else:
    PY3 = False

# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))

Load_Failed = object()
""" unique object to mark failure condition."""


def refloader(key, mapping, remove=True):
    """ Generates key-value pair out of a map containing name-content
    pairs, by referencing.

    Subclasses should override this function unless this name space
    contains the same kind of items in `default`

    Parameters
    ----------
    mapping : dict
        a map containing name-content pairs (such as `default`, `initial`).

    Returns
    -------
    dict:
       key and load-result pairs. load-result is `Load_Failed` if loading of the key was not successful.
    """

    res = mapping.get(key, Load_Failed)
    if remove and res is not Load_Failed:
        del mapping[key]
    # return key in the mapping and the load result.
    return {key: res}


class NameSpace_meta(type):
    """ metaclass for name-spaces such as class white list and schemas.

    Ref 'classproperty'.   # https://stackoverflow.com/a/1800999
    """

    sources = [{}]
    """ name-content list from the main package and for plug-in/app."""

    def __new__(metacls,  clsname, bases, attrs,
                sources=None,
                extensions=None,
                load=None, **kwds):
        """ Internal map is initialized with `sources`.

        The internal map is initialized with a `default` and a list of `extension` maps which can be collection of key-value pairs. These maps are put into the `sources` map. However these maps are only the information needed to populate the main map, the target map of namespace.
The target namespace is also represented by a collection of key-value pairs but each of them reside in a cache map, and are loaded into the cache map by the `load` function lazily when the key is used. The default `refloader` just copy the reference of the values in the `sources` map by the same name.
This architecture allows expensive values to be associated with names gradually in a cache in a pay-as-you-need manner.

        Examples
        --------
        .. code-bloc::

        For an app package with many classes:

        Import user classes in a python file for example projectclasses.py:
        .. code-bloc::

        clz_map = {
                'MyClass1': 'mypackage.mymodule',
                'MyClass2': 'mypackage.mymodule'
        }

        # from yet another module defining a dict of Class_name: Class_obj pairs

        try:
            from mypackage.mymodule import pairs
        except (ImportError, ModuleNotFoundError) as e:
            logger.info(e)
            raise

        import fdi.dataset.namespace import NameSpace_meta
        import Reverse_Modules_Classes

        def loader():
            ...

        Class PC(metaclass=NameSpace_meta,
                  sources=[Reverse_Modules_Classes, pairs, clz_map],
                  load=loader
                  ):
              pass

        prjcls = PC.mapping

        new_instance = prjcls['MyClass1']

        Define new classes and update `PC`::

        class Myclass():
              ...

        PC.update({'foo': MyClass})

        and use::

        ``new_instance = PC.mapping['foo']``

        Parameters
        ----------
        clsname: str
            Name of the class being defined(Event in this example)
        bases: tuple
            Base classes of the constructed class, empty tuple in this case
        attrs: dict
            Dict containing methods and fields defined in the class
        sources: list
            A list of maps containing the core/platform/framework/primary package namespace and plug-in/application package name spaces.
        extensions: list
            A list of key-value maps to extend the `cache`.
        load: function
            classmethod to load a key from `initial` of the internal map.
        kwds: dict
            member `key`-`val` pairs: `k` will be added to instance-classes' class attributes namespace, initiated to `val`

        Returns
        -------
        cls
            new class
        """
        new_cls = super().__new__(metacls, clsname, bases, attrs)

        if sources is None:
            sources = metacls.sources
        if load is None:
            # defined in this module
            load = refloader
        nm = Lazy_Loading_ChainMap(*sources, extensions=extensions, load=load)
        if kwds:
            for name, value in kwds.items():
                setattr(new_cls, name, value)
        logger.debug('***maps*** %s' % str(sources)[:300])
        new_cls._the_map = nm
        new_cls.mapping = nm

        logger.debug("New class made with metaclass %s: _the_map 0x%x, sources %d, initial %d, cache %d. load %s, kwds %s,initial=%s..." %
                     (metacls.__name__,
                      id(nm),
                      len(nm.sources),
                      len(nm.initial),
                      len(nm.cache),
                      str(load)[:300],
                      str(kwds)[:300],
                      str(nm.initial)[:300]
                      ))
        return new_cls

    def clear(cls):
        """ Empty the internal mapping including `maps[1:]`.

        `sources` map is not wiped.

        """
        for m in cls._the_map.maps:
            m.clear()

    def update(cls, *args, **kwds):
        """ Updates the mapping.

        Parameters
        ----------
        c: Mapping to be used to update the main map with. Subclasses that need to
        load must format key and values as required.

        Returns
        -------
        dict: The mapping.

        """
        cls._the_map.update(*args, **kwds)
        return cls._the_map

    def reload(cls):
        """ re-import classes in the map.

        """

        cls._the_map.reload()
        return cls._the_map


class Lazy_Loading_ChainMap(ChainMap):

    # failed = {}
    # """ name-content pairs of the unloadable pairs from `default`. """

    cache = {}
    """ for the loaded key-vals. """

    default = {}
    """ This mapping stores name-content pairs that are used to
    build the main map, which is located in the ```lru_cache``` of
    ```__getitem__```. Example: module_name-classe_names, schema
    store."""

    def __init__(self, *args, extensions=None, load=None, **kwds):
        if extensions is None:
            extensions = []
        if load is None:
            load = refloader
        self.extenions = extensions
        self.load = load
        self.sources = ChainMap(*args, **kwds)
        self.initial = dict(self.sources)
        super().__init__(self.cache, self.initial, *extensions)

        logger.debug("New LLC %s initialized: _the_map 0x%x sources %d, initial %d, cache %d. extensions %d. initial=%s..." %
                     (self.__class__.__name__,
                      id(self),
                         len(self.sources),
                         len(self.initial),
                         len(self.cache),
                         len(self.extenions),
                         str(self.initial)[:300]
                      ))

    def __getitem__(self, key):
        for m in self.maps:
            if m is self.initial:
                loaded = self.load(key, self.initial, remove=True)
                for k, re in loaded.items():
                    if k == key:
                        res = re
                    if re is not Load_Failed:
                        # success. put into cache
                        self.cache[k] = re
                    else:
                        #  ignore to let future calls try.
                        pass

                if res is not Load_Failed:
                    return res
            else:
                # in the cache?
                if key in m:
                    return m[key]
        res = None

    def __setitem__(self, key, value):

        if key in self.initial:
            self.initial.__delitem__(key)
        self.cache.__setitem__(key, value)
        return

    def add_ns(self, ns=None, order=0):
        """ Add new name space in the list of internal ones.

        Parameters
        ----------
        order: int
            The number of maps to look up before this one is . If negative, `-n
 ` means the n-th from the last. E.g. `order=-1` means to become the last one.
        ns: mapping
            Namespace map to be looked up.
        """
        if ns is None:
            ns = {}
        if order == -1:
            self.maps.append(ns)
        elif order < -1:
            self.maps.insert(order+1, ns)
        else:
            self.maps.insert(order, ns)

    def update(self, c=None, exclude=None, verbose=False,
               extension=None, ignore_error=False,
               ):
        """ Updates the mapping.

        Parameters
        ----------
        c: mapping
            to be used to update with. Subclasses that need to
        load must format key and values as required.
        exclude: boolean
            Ignore these keys when updating.
        extension: mapping
            add `c` as a new sources map.

        Returns
        -------
        dict: The mapping.

        """
        if exclude is None:
            exclude = []
        cc = copy.copy(c)
        if cc:
            for x in exclude:
                cc.pop(x, None)
            if extension:
                self.sources.maps.insert(0, cc)
            else:
                ini = self.initial
                in_initial = set(cc.keys()) & set(ini.keys())
                for i in in_initial:
                    ini.__delitem__(i)
                self.cache.update(cc)
        return self

    def reload(self):
        """ replenish the `initial` map, empty other map.

        Parameters
        ----------

        Returns
        -------
        ChainMap:
            `self`.
        """

        self.clear()
        self.initial.update(self.sources)
        return self