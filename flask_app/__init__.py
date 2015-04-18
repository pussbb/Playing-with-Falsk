# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import os
import traceback

from flask import Flask, current_app, request
from flask_bootstrap3 import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from flask_app.controllers import Controller

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

@APP.errorhandler(Exception)
def exception_handler(exception=None):
    """Catch all exception and output them in requested format

    """
    print(exception)
    if isinstance(exception, RequestRedirect):
        return exception.get_response(current_app)

    msg = str(exception)
    code = 500
    if isinstance(exception, HTTPException):
        code = exception.code
    if current_app.config['DEBUG']:
        msg = traceback.format_exc()
    current_app.logger.error(str(request))
    current_app.logger.exception(exception)
    return Controller.Response.as_requested(msg, code)
