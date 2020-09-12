# -*- coding: utf-8 -*-

import traceback
import logging


# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))


def trbk(e):
    """ trace back
    """
    ls = [x for x in traceback.extract_tb(e.__traceback__).format()] if hasattr(
        e, '__traceback__') else ['']
    return ' '.join(ls) + ' ' + \
        (e.child_traceback if hasattr(e, 'child_traceback') else '')


def trbk2(e):
    tb = traceback.TracebackException.from_exception(e)
    return ''.join(tb.stack.format())


def exprstrs(self, v='_value'):
    """ Generates a set of strings for expr() """

    if hasattr(self, v):
        val = getattr(self, v)
        if hasattr(self, '_type'):
            vs = hex(val) if self._type == 'hex' and issubclass(
                val.__class__, int) else str(val)
            ts = str(self._type)
        else:
            vs = str(val)
            ts = 'unknown'
    else:
        vs = 'unknown'
        if hasattr(self, '_type'):
            ts = str(self._type)
        else:
            ts = 'unknown'

    ds = str(self.description) if hasattr(
        self, 'description') else 'unknown'
    fs = str(self._default) if hasattr(self, '_default') else 'unknown'
    gs = str(self._valid) if hasattr(self, '_valid') else 'unknown'
    us = str(self._unit) if hasattr(self, '_unit') else 'unknown'
    cs = str(self._typecode) if hasattr(self, '_typecode') else 'unknown'

    return (vs, us, ts, ds, fs, gs, cs)


def pathjoin(*p):
    """ join path segments with given separater (default '/').
    Useful when '\\' is needed.
    """
    sep = '/'
    r = sep.join(p).replace(sep+sep, sep)
    #print(p, r)
    return r


bldins = str.__class__.__module__


def fullname(obj):
    """ full class name with module name.

    https://stackoverflow.com/a/2020083/13472124
    """
    t = type(obj) if not isinstance(obj, type) else obj
    module = t.__module__
    if module is None or module == bldins:
        return t.__name__  # Avoid reporting __builtin__
    else:
        return module + '.' + t.__name__


def lls(s, length=80):
    """ length-limited string
    """
    st = str(s)
    if len(st) <= length:
        return st
    else:
        return st[:length - 3] + '...'
