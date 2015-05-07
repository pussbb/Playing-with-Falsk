# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import os


class Config(object):
    DEBUG = False
    TESTING = False
    STRICT_SLASHES = False
    PORT = 5050
    APPLICATION_ROOT = '/'
    PROFILE = False
    PROFILE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'profile')

    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = False
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    SECRET_KEY = 'dF=DL2)DWJ2)+OKaUP3Tz!b;n&Ns/$qxT7aeg!~;FVAcVnM[HV;4m:U/=wmP}S?R'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
