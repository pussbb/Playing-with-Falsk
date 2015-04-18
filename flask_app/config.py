# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division


class Config(object):
    DEBUG = False
    TESTING = False
    STRICT_SLASHES = False
    PORT = 5050
    APPLICATION_ROOT = '/v1'

    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = False
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_POOL_RECYCLE = 15*60
    SQLALCHEMY_POOL_TIMEOUT= 15*60

    SQLALCHEMY_DATABASE_URI="sqllite://site.db"


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
