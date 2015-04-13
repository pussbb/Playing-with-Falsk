# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask import current_app

from .controllers import welcome, build


welcome.Welcome.register()
build.Build.register()

from .blueprint.test.init import register_blueprint
register_blueprint(current_app)

