# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask import current_app
from flask_app.controllers import Controller, get_method
from flask_app.helpers.app import create_blueprint


class Test(Controller):
    ROUTE_BASE = ''

    @get_method('/hi/')
    def index(self):
        return self.render_view("test.html", {})


def register_blueprint(app=current_app):
    controllers = [Test]
    create_blueprint(app, 'test', __name__, controllers=controllers,
                     register=True)
