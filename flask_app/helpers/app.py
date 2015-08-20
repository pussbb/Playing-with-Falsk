# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import importlib

import os
import traceback
import warnings
from flask import Blueprint, current_app, request
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from ..controller import Controller

from .url import app_root_url


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


def import_blueprints(app):
    folder_name = app.config.get('BLUEPRINTS_FOLDER', 'blueprints')
    folder = os.path.join(app.root_path, folder_name)
    if not os.path.isdir(folder):
        return

    dir_path, dirs, _ = next(os.walk(folder))
    base_module = '.'.join([app.name, folder_name])
    for dir_name in dirs:
        try:
            module = importlib.import_module(
                '.'.join([base_module, dir_name, 'blueprint'])
            )
        except ImportError as _:
            warnings.warn("Module {0} is not blueprint".format(dir_name))
        else:
            module.register_blueprint(app)


def simple_exception_handler(exception=None):
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
    return Controller.Response.to_plain(msg, code)

