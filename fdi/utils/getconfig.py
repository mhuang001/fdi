# -*- coding: utf-8 -*-

from os.path import join, expanduser, expandvars, is_dir
import functools
import sys

import logging
# create logger
logger = logging.getLogger(__name__)
#logger.debug('logging level %d' % (logger.getEffectiveLevel()))


class Instance():

    def get(self, name=None, conf='pns'):
        if name:
            try:
                return self._cached_conf
            except AttributeError:
                self._cached_conf = getConfig(name=name, conf=conf)
                return self._cached_conf
        else:
            try:
                return self._cached_poolurl
            except AttributeError:
                self._cached_poolurl = getConfig(name=name, conf=conf)
                return self._cached_poolurl


# @functools.lru_cache(8)
def getConfig(name=None, conf='pns'):
    """ Imports a dict named [conf]config.

    The contents of the config are defined in the ``.config/[conf]local.py`` file. The contenss are used to update defaults in ``fdi.pns.config``.
    Th config file is given by the environment variable ``CONF_DIR``, which if  not given or pointing to an existing directly is process owner's ``~/.config`` directory.

    name: if given the poolurl in ``poolurl_of`` is returned, else construct a poolurl from the contents in dict <conf>config.
    conf: configuration ID. default 'pns', so the file is 'pnslocal.py'.
    """
    # default configuration is provided. Copy pns/config.py to ~/.config/pnslocal.py
    config = {}

    epath = expandvars('$CONF_DIR')
    if is_dir(epath):
        confp = epath
    else:
        env = expanduser(epath)
        # apache wsgi will return '$HOME' with no expansion
        if env == '$HOME':
            env = '/root'
        confp = join(env, '.config')
    sys.path.insert(0, confp)
    # this is the var_name part of filename and the name of the returned dict
    var_name = conf+'config'
    module_name = conf+'local'
    file_name = module_name + '.py'
    logger.info('Reading from configuration file %s/%s.py' %
                (confp, file_name))

    try:
        c = __import__(module_name, globals(), locals(), [stem], 0)
        logger.debug('Reading %s/%s.py done.' % (confp, file_name))
        config.update(c.__dict__[var_name])
    except ModuleNotFoundError as e:
        logger.warning(str(
            e) + '. Use default config in the package, such as fdi/pns/config.py. Copy it to ~/.config/[package]local.py and make persistent customization there.')

    if name:
        urlof = vars(c)['poolurl_of']
        if name in urlof:
            return urlof[name]
        else:
            return config['httphost'] + config['baseurl'] + '/' + name
    else:
        return config
