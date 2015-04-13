# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
from flask import Blueprint, current_app
from flask_app.controllers import Controller, get_method
from flask_app.helpers.url import reduce_slashes, app_root_url


class Test(Controller):
    @get_method('/hi/')
    def index(self):
        return "888"


def register_blueprint(app=current_app):
    prefix = app.config.get('APPLICATION_ROOT', '/') or '/'
    prefix = app_root_url(app, 'test/')
    test = Blueprint('test', __name__, url_prefix=prefix)
    Test.register(app=test)
    app.register_blueprint(test)
