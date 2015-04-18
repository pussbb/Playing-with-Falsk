# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import os

from flask import Flask
from flask_bootstrap3 import Bootstrap
from flask_sqlalchemy import SQLAlchemy

APP_NAME = __name__.split('.')[0]
OS_ENV_SETTINGS_KEY = '{0}_SETTINGS'.format(APP_NAME)

APP = Flask(__name__.split('.')[0], instance_relative_config=True)


def init_app_settings(config_name=None):
    if config_name is not None:
        os.environ[OS_ENV_SETTINGS_KEY] = config_name
    config = '{0}.config.{1}Config'.format(
        APP_NAME,
        os.environ.get(OS_ENV_SETTINGS_KEY, 'Production')
    )

    APP.config.from_object(config)

init_app_settings()
DB = SQLAlchemy(APP)
Bootstrap(APP)
with APP.app_context():
    from . import routes


def serve(config_env="Development"):
    if config_env:
        init_app_settings(config_env)
    APP.run()


