# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division


from flask_app.controller import Controller, get_method

from flask_app.helpers.url import build_url


class Build(Controller):

    @get_method('/hello')
    def index(self):
        return build_url('test.Test:index')


