# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask import Flask
from flask_bootstrap3 import Bootstrap
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


def create_app(mode='Development'):
    app = Flask(__name__.split('.')[0], instance_relative_config=True)
    Bootstrap(app)
    app.config.from_object('{0}.config.{1}Config'.format(__name__, mode))
    DB.init_app(app)

    with app.app_context():
        from . import routes

    return app


def serve(mode='Development'):
    create_app(mode).run()


