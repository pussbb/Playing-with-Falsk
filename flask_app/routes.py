# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from .controllers import welcome, build


welcome.Welcome.register()
build.Build.register()