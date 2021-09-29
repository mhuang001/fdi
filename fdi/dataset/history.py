# -*- coding: utf-8 -*-

from .odict import ODict
from .finetime import FineTime, utcobj
from .dataset import CompositeDataset
from .eq import DeepEqual, deepcmp
from collections import OrderedDict

import logging
# create logger
logger = logging.getLogger(__name__)
# logger.debug('level %d' %  (logger.getEffectiveLevel()))


class History(CompositeDataset):
    """ Public interface to the history dataset. Contains the
    main methods for retrieving a script and copying the history.
    """

    def __init__(self, other=None, **kwds):
        """
        mh: The copy constructor is better not be implemented. Use copy()
        instead. Remember: not only copies the datasets,
        but also changes the history ID in the metadata and
        relevant table entries to indicate that this a new
        independent product of which the history may change.

        Parameters
        ----------

        Returns
        -------

        """
        super(History, self).__init__(**kwds)

        # Name of the table which contains the history script
        self.HIST_SCRIPT = ''

        # Name of the parameter history table
        self.PARAM_HISTORY = ''
        # Name of the task history table
        self.TASK_HISTORY = ''

    def accept(self, visitor):
        """ Hook for adding functionality to meta data object
        through visitor pattern.

        Parameters
        ----------

        Returns
        -------

        """
        visitor.visit(self)

    def getOutputVar(self):
        """ Returns the final output variable of the history script.

        Parameters
        ----------

        Returns
        -------

        """
        return None

    def getScript(self):
        """ Creates a Jython script from the history.

        Parameters
        ----------

        Returns
        -------

        """
        return self.HIST_SCRIPT

    def getTaskHistory(self):
        """ Returns a human readable formatted history tree.

        Parameters
        ----------

        Returns
        -------

        """
        return self.TASK_HISTORY

    def saveScript(self, file):
        """ Saves the history script to a file.

        Parameters
        ----------

        Returns
        -------

        """

    def __getstate__(self):
        """ Can be encoded with serializableEncoder

        Parameters
        ----------

        Returns
        -------

        """
        return OrderedDict(
            _ATTR_PARAM_HISTORY=self.PARAM_HISTORY,
            _ATTR_TASK_HISTORY=self.TASK_HISTORY,
            _ATTR_meta=self._meta,
            **self.data,
            _STID=self._STID)
