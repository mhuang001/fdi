# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ProductrefResult(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, urnobj: str=None, meta: ProductMeta=None):  # noqa: E501
        """ProductrefResult - a model defined in Swagger

        :param urnobj: The urnobj of this ProductrefResult.  # noqa: E501
        :type urnobj: str
        :param meta: The meta of this ProductrefResult.  # noqa: E501
        :type meta: ProductMeta
        """
        self.swagger_types = {
            'urnobj': str,
            'meta': ProductMeta
        }

        self.attribute_map = {
            'urnobj': 'urnobj',
            'meta': 'meta'
        }

        self._urnobj = urnobj
        self._meta = meta

    @classmethod
    def from_dict(cls, dikt) -> 'ProductrefResult':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The productref_result of this ProductrefResult.  # noqa: E501
        :rtype: ProductrefResult
        """
        return util.deserialize_model(dikt, cls)

    @property
    def urnobj(self) -> str:
        """Gets the urnobj of this ProductrefResult.

        URN  # noqa: E501

        :return: The urnobj of this ProductrefResult.
        :rtype: str
        """
        return self._urnobj

    @urnobj.setter
    def urnobj(self, urnobj: str):
        """Sets the urnobj of this ProductrefResult.

        URN  # noqa: E501

        :param urnobj: The urnobj of this ProductrefResult.
        :type urnobj: str
        """
        if urnobj is None:
            raise ValueError("Invalid value for `urnobj`, must not be `None`")  # noqa: E501

        self._urnobj = urnobj

    @property
    def meta(self) -> ProductMeta:
        """Gets the meta of this ProductrefResult.


        :return: The meta of this ProductrefResult.
        :rtype: ProductMeta
        """
        return self._meta

    @meta.setter
    def meta(self, meta: ProductMeta):
        """Sets the meta of this ProductrefResult.


        :param meta: The meta of this ProductrefResult.
        :type meta: ProductMeta
        """
        if meta is None:
            raise ValueError("Invalid value for `meta`, must not be `None`")  # noqa: E501

        self._meta = meta