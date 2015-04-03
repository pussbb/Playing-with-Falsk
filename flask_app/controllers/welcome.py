# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from . import Controller, route, http_method_route, JsonResponce, XmlResponse


class Welcome(Controller):

    @http_method_route('/<int:ddd>')
    def post(self, ddd):
        return XmlResponse({'asa': 'dfd'}, 200)

    @http_method_route('/', defaults={'ddd': None})
    @http_method_route('/<int:ddd>')
    def get(self, ddd):
        return {}, 200

    @http_method_route('/<int:ddd>')
    def prepost(self, ddd):
        return {}, 200

    @route('/welcome')
    @route('/')
    def index(self):
        return self.render_view('index.html', {'title': "Index"})

    @route('/about-us')
    def about_us(self):
        return self.render_view('index.html', {'title': "About US"})
