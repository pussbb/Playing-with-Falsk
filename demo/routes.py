# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask import current_app

from .controllers import build, welcome
from flask_app.helpers.app import import_blueprints

welcome.WelcomeSTr.register()
build.Build.register()

import_blueprints(current_app)
