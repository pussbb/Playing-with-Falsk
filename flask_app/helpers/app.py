# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
from flask import Blueprint
from flask_app.helpers.url import app_root_url


def create_blueprint(app, name, import_name, controllers=[], register=False,
                     **kwargs):
    if 'url_prefix' not in kwargs:
        kwargs['url_prefix'] = app_root_url(app, name+'/')

    if 'template_folder' not in kwargs:
        kwargs['template_folder'] = 'templates'

    if 'static_folder' not in kwargs:
        kwargs['static_folder'] = 'static'

    blueprint = Blueprint(name, import_name, **kwargs)

    for controller in controllers:
        controller.register(app=blueprint)

    if register:
        app.register_blueprint(blueprint)

    return blueprint
