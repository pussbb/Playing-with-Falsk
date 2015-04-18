# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from . import Controller, route, post_method, http_method, JsonResponse, \
    XmlResponse, get_method
from pydoc import render_doc, doc, plain
from flask import current_app
from werkzeug.utils import redirect
from flask_app.helpers.url import build_url


class Welcome(Controller):

    ROUTE_BASE = ''

    def _before(self, *args, **kwargs):
        print(args)

    @http_method('/<int:ddd>')
    def post(self, ddd=0):
        """

        :param ddd:
        :return:
        """
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
        """

        :return:
        """
        return redirect(build_url('Welcome:about_us'))
        #return self.render_view('index.html', {'title': "Index"})

    @post_method('/post')
    def some_function(self):
        return self.response.empty()  # .as_requested({}, 200)

    @route('/about-us')
    def about_us(self):
        return self.render_view('index.html', {'title': "About US"})

    @get_method('/docs')
    def docs(self):
        def routes():
            for key, view_function in current_app.view_functions.items():
                yield (key, plain(render_doc(view_function, title="%s")))

        return self.render_view('docs.html', {'gen_docs': routes()})
