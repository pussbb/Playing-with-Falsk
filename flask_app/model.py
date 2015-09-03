# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

import datetime
import inspect
from decimal import Decimal
from sqlalchemy import event
from sqlalchemy.orm.attributes import InstrumentedAttribute
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

        if not hasattr(self, attr):
            return ''
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
        if not hasattr(cls, '__wrapped_readonly__'):
            for model_event in ['insert', 'delete', 'update']:
                event.listen(cls, "before_{0}".format(model_event),
                             cls.__raise_exception)

            attributes = inspect.getmembers(
                cls,
                lambda x: isinstance(x, InstrumentedAttribute)
            )
            for attr_name, attr in attributes:
                for attr_event in ['append', 'set', 'remove']:
                    event.listen(attr, attr_event, cls.__read_only_column)
            cls.__wrapped_readonly__ = True

        return super(BaseReadOnlyModel, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def __raise_exception(cls, *args, **kwargs):
        raise Exception('{0} Read only model'.format(cls.__name__))

    @classmethod
    def __read_only_column(cls, *args, **kwargs):
        raise Exception('{name}.{key} is read only column'.format(
            key=args[-1].key,
            name=cls.__name__
        ))
