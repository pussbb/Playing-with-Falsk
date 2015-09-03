# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask_bootstrap3 import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import flask_app
from flask_app.helpers.app import simple_exception_handler

APP = flask_app.create_app(flask_app.from_module_name(__name__))
DB = SQLAlchemy(APP)

Bootstrap(APP)
with APP.app_context():
    from . import routes


from .models.user import User, UserSettings


def serve(app_env=None):
    flask_app.serve(APP, app_env)


@APP.errorhandler(Exception)
def handler(*args, **kwargs):
    return simple_exception_handler(*args, **kwargs)
