# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import traceback
import os
import warnings

from flask import Flask, send_from_directory

try:
    from werkzeug.contrib.lint import LintMiddleware
except ImportError as _:
    LintMiddleware = None
    warnings.warn("Lint is not available " + traceback.format_exc())

try:
    from werkzeug.contrib.profiler import ProfilerMiddleware
except ImportError as _:
    ProfilerMiddleware = None
    warnings.warn(
        "ProfilerMiddleware is not available" + traceback.format_exc()
    )

OS_ENV_SETTINGS_KEY_TEMPLATE = '{app_name}_SETTINGS'


def from_module_name(name=__name__):
    return name.split('.')[0]


def init_app_settings(app, config_name=None):
    os_env_settings_key = OS_ENV_SETTINGS_KEY_TEMPLATE.format(
        app_name=app.name
    ).upper()

    if config_name is not None:
        os.environ[os_env_settings_key] = config_name
    config = '{0}.config.{1}Config'.format(
        app.name,
        os.environ.get(os_env_settings_key, 'Production')
    )

    app.config.from_object(config)


def create_app(app_name, config_name=None, **app_kwargs):
    app = Flask(app_name, instance_relative_config=True, **app_kwargs)
    init_app_settings(app, config_name)

    favicon_icon_path = os.path.join(app.root_path, 'static')
    if not os.path.isfile(os.path.join(favicon_icon_path, 'favicon.ico')):
        favicon_icon_path = app.root_path

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(favicon_icon_path, 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    #if app.debug and LintMiddleware:
    #    app.wsgi_app = LintMiddleware(app.wsgi_app)

    if app.config.get('PROFILE', False) and ProfilerMiddleware:
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            profile_dir=app.config.get('PROFILE_DIR', None)
        )

    return app


def serve(app, app_env=None):
    if app_env:
        init_app_settings(app, app_env)
    app.run('0.0.0.0', app.config.get('PORT', None))
