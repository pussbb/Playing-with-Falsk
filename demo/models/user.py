# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from . import DbModel, DB, ReadOnly
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class User(DbModel):
    __tablename__ = 'users'
    EXTRA_FIELDS = ['full_name', 'settings']
    id = DB.Column(DB.Integer, primary_key=True)
    _username = DB.Column(DB.String(80), unique=True)
    email = DB.Column(DB.String(120), unique=True)
    settings = relationship('UserSettings', uselist=False, backref=backref(__tablename__))

    @property
    def full_name(self):
        return '<{0}> {1}'.format(self.username, self.email)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, val):
        self._username = val


class UserSettings(DbModel):
    __tablename__ = 'user_settings'
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, ForeignKey('users.id'))
    user = relationship('User', uselist=False, backref=backref(__tablename__, ))
    properties = DB.Column(DB.String)
