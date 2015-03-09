# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from . import Controller, route, api_route

class Welcome(Controller):

    @api_route('/<int:ddd>')
    def post(self, ddd):
        return {}, 200

    @api_route('/<int:ddd>')
    def get(self, ddd):
        return {}, 200

    @api_route('/<int:ddd>', methods=['PREPOST'])
    def prepost(self, ddd):
        return {}, 200

    @route('/')
    def index(self):
        return self.render_view('index.html', {'title': "Index"})

    @route('/about-us')
    def about_us(self):
        return self.render_view('index.html', {'title':"About US"})
