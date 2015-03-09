# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division


import collections
from functools import wraps
import inspect
import os
import sys

from flask import request, Response, render_template, make_response, jsonify, current_app
from werkzeug.exceptions import NotImplemented as HTTPNotImplemented
from flask.views import MethodView

import json
import re
from simplexml import dumps



if sys.version_info[0] > 3:
    basestring = unicode


def route(*args, **kwargs):
    def real_wrapper(func):
        func._route = (args, kwargs)
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapper
    return real_wrapper

def api_route(*args, **kwargs):
    def real_wrapper(func):
        func._api_route = (args, kwargs)
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapper
    return real_wrapper

class ControllerRoute(object):

    @classmethod
    def register(cls, app=current_app, *class_args, **class_kwargs):
        predict = lambda x: inspect.ismethod(x) or inspect.isfunction(x)
        for method in inspect.getmembers(cls, predict):
            if hasattr(method[-1], '_route'):
                cls.add_method_to_route(method, app, *class_args,
                                        **class_kwargs)
            elif hasattr(method[-1], '_api_route') and cls.api_enabled:
                route, route_data = getattr(method[-1], '_api_route')
                cls.add_route(app, route[0], cls.as_view( str("{0}:{1}".format(cls.__name__,
                                                          method[0]))),
                              route_data)

    @classmethod
    def add_method_to_route(cls, method, app=current_app, *class_args,
                            **class_kwargs):

        route, route_data = getattr(method[-1], '_route')
        def proxy(*args, **kwargs):
            kwargs['__func'] = method[0]
            return cls(*class_args, **class_kwargs).dispatch_request(*args,
                                                                     **kwargs)

        if cls.decorators:
            for decorator in cls.decorators:
                proxy = decorator(proxy)

        if not route_data.get('endpoint'):
            route_data['endpoint'] = str("{0}:{1}".format(cls.__name__,
                                                          method[0]))
        cls.add_route(app, route[0], proxy, route_data)


    @classmethod
    def add_route(cls, app, route, view_func, route_data={}):
        route_base = cls.route_base or ''
        base_url = app.config.get('APPLICATION_ROOT', '/') or '/'
        uri = "{app_root}/{route_base}{route}".format(app_root=base_url,
                                                      route_base=route_base,
                                                      route=route)
        app.add_url_rule(ControllerRoute.reduce_slashes(uri),
                                 view_func=view_func, **route_data)

    @staticmethod
    def reduce_slashes(url):
        """Reduce slashes in url

        :param url:
        :return:
        """
        return re.sub(r'(?<!:)\/\/+', '/', url)


class Controller(MethodView, ControllerRoute):

    route_base = None

    api_enabled = True

    def dispatch_request(self, *args, **kwargs):
        response = None
        if kwargs.get('__func'):
            func = kwargs.get('__func')
            del kwargs['__func']
            response = getattr(self, func)(*args, **kwargs)
        else:
            try:
                response = super(Controller, self).dispatch_request(*args,
                                                                    **kwargs)
            except AssertionError, exception:
                raise HTTPNotImplemented(exception)

        if isinstance(response, Response):
            return response

        if not isinstance(response, (list, set, tuple)):
            response = [response, 500]

        if not isinstance(response[0], collections.Iterable):
            return Response(*response)

        return self.__make_response(*response)

    def __make_response(self, *args, **kwargs):
        accept_header = request.headers.get('content-type')
        if not accept_header:
            accept_header = request.headers.get('accept').split(',')[0]

        if accept_header == 'application/json':
            return self.json_response(*args, **kwargs)
        if accept_header == 'application/xml':
            return self.xml_response(*args, **kwargs)
        return  make_response(*args, **kwargs)

    def json_response(self, data, code=200, *args, **kwargs):
        ''' Return application/json

        '''
        if isinstance(data, dict):
            data = jsonify(data)
        else:
            data = json.dumps(data, indent=2)
        resp = make_response(data, code, *args, **kwargs)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    def xml_response(self, data, code=200, *args, **kwargs):
        ''' Return application/xml

        '''
        resp = make_response(dumps({'response': data}), code, *args, **kwargs)
        resp.headers['Content-Type'] = 'application/xml'
        return resp

    def render_view(self, name, view_data, status=200, *args, **kwargs):
        parts = re.split(r'([A-Z][a-z]+)+', self.__class__.__name__)
        parts = map(lambda x:x.lower(), filter(None, parts))
        parts.append(name)
        return make_response(
            render_template(os.path.join(*parts), **view_data),
            status,
            *args,
            **kwargs
        )

    @property
    def request_values(self):
        return request.values
