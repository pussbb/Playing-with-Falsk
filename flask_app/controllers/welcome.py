# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from . import Controller, route, post_method, http_method, JsonResponse, \
    XmlResponse


class Welcome(Controller):

    ROUTE_BASE = ''

    def _before(self, *args, **kwargs):
        print(args)

    @http_method('/<int:ddd>')
    def post(self, ddd=0):
        return XmlResponse({'asa': 'dfd'}, 200)

    @http_method('/', defaults={'ddd': None})
    @http_method('/<int:ddd>')
    def get(self, ddd):
        return {}, 200

    @http_method('/<int:ddd>')
    def prepost(self, ddd):
        return {}, 200

    @route('/welcome')
    @route('/')
    def index(self):
        return self.render_view('index.html', {'title': "Index"})

    @post_method('/post')
    def some_function(self):
        return self.response.empty()  # .as_requested({}, 200)

    @route('/about-us')
    def about_us(self):
        return self.render_view('index.html', {'title': "About US"})
