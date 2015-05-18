# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

import datetime
from decimal import Decimal
from sqlalchemy import event
from sqlalchemy_utils import Choice


class BaseModel(object):

    EXTRA_FIELDS = []

    def dump(self, additional_fields=[]):
        """SqlAlchemy object to dict

        """
        result = {column: self.__get_attr(column) for column in self}
        for field in set(additional_fields + self.EXTRA_FIELDS):
            result[field] = self.__get_attr(field)
        return result

    def __iter__(self):
        for column in self.__table__.columns:
            yield (column.name,)[0]

    def __getstate__(self):
        """ for pickle dumps

        :return: dict state
        """
        return dict(self.dump())

    def items(self):
        for column in self:
            yield column, getattr(self, column)

    def __get_attr(self, attr):
        """Format values if needed

        """
        value = getattr(self, attr)
        val_type = type(value)
        if val_type in (datetime.datetime, datetime.date, Decimal):
            return str(value)
        elif val_type is Choice:
            value = value.value

        return value

    @classmethod
    def find(cls, id=None, **criterion):
        if id:
            criterion['id'] = id
        return cls.query.filter_by(**criterion).one()

    @classmethod
    def find_all(cls, **criterion):
        return cls.query.filter_by(**criterion)

class BaseReadOnlyModel(BaseModel):

    def __new__(cls, *args, **kwargs):
        obj = super(BaseReadOnlyModel, cls).__new__(cls, *args, **kwargs)

        for model_event in ['before_insert', 'before_delete', 'before_update']:
            event.listen(obj.__class__, model_event, obj.raise_exception)

        for column in obj.__table__.columns:
            item = getattr(obj.__class__, column.name)
            for attr_event in ['append', 'set', 'remove']:
                event.listen(item, attr_event, obj.read_only_column)

        return obj

    def raise_exception(self, *args, **kwargs):
        raise Exception('Read only model')

    def read_only_column(self, *args, **kwargs):
        raise Exception('{key} is read only column'.format(key=args[-1].key))
