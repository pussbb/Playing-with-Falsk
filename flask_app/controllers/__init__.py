# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division


import collections
from functools import wraps
import inspect
import os

from flask import request, Response, render_template, make_response, jsonify, current_app
from werkzeug.exceptions import NotImplemented as HTTPNotImplemented
from flask.views import MethodView

import json
import re
from simplexml import dumps as xml_dumps
from ..helpers.url import reduce_slashes


def __real_wrapper(attr, rule, **kwargs):
    def real_wrapper(func):
        func_attr = getattr(func, attr, [])
        func_attr.append((rule, kwargs))
        setattr(func, attr, func_attr)

        @wraps(func)
        def wrapper(self, *func_args, **func_kwargs):
            return func(self, *func_args, **func_kwargs)
        return wrapper

    return real_wrapper


def route(rule, **kwargs):
    return __real_wrapper('_route', rule, **kwargs)


def get_method(rule, **kwargs):
    kwargs['methods'] = ['GET']
    return route(rule, **kwargs)


def post_method(rule, **kwargs):
    kwargs['methods'] = ['POST']
    return route(rule, **kwargs)


def delete_method(rule, **kwargs):
    kwargs['methods'] = ['DELETE']
    return route(rule, **kwargs)


def put_method(rule, **kwargs):
    kwargs['methods'] = ['PUT']
    return route(rule, **kwargs)


def http_method_route(rule, **kwargs):
    return __real_wrapper('_http_method_route', rule, **kwargs)


class ControllerResponse(Response):

    def __new__(cls, *args, **kwargs):
        kwargs.pop('mimetype', None)
        kwargs.pop('content_type', None)
        headers = kwargs.pop('headers', {})
        if headers:
            headers.pop('Content-Type', None)
            kwargs['headers'] = headers
        return super(ControllerResponse, cls).__new__(cls, *args, **kwargs)


class XmlResponse(ControllerResponse):

    default_mimetype = 'text/xml'

    def __init__(self, data, *args, **kwargs):
        super(XmlResponse, self).__init__(xml_dumps({'root': data}),
                                          mimetype='application/xml',
                                          content_type='application/xml',
                                          *args, **kwargs)


class PlainResponse(ControllerResponse):

    default_mimetype = 'text/plain'


class JsonResponse(ControllerResponse):

    default_mimetype = 'application/json'

    def __init__(self, data, *args, **kwargs):
        super(JsonResponse, self).__init__(json.dumps(data, indent=2),
                                           mimetype='application/json',
                                           content_type='application/json',
                                           *args, **kwargs)


class ControllerRoute(object):

    @classmethod
    def register(cls, app=current_app, *class_args, **class_kwargs):
        predict = lambda x: inspect.ismethod(x) or inspect.isfunction(x)

        for func_name, func in inspect.getmembers(cls, predict):
            for item in getattr(func, '_route', []):
                cls.add_method_to_route(func_name, item, app, *class_args,
                                        **class_kwargs)
            for item in getattr(func, '_http_method_route', []):
                rule, kwargs = item
                kwargs['methods'] = [func_name.upper()]
                view_func = app.view_functions.get(kwargs.get('endpoint')) or \
                            app.view_functions.get(cls.__name__)

                if not view_func:
                    view_func = cls.as_view(cls.__name__, *class_args,
                                            **class_kwargs)

                cls.add_route(app, rule, view_func, **kwargs)

    @classmethod
    def add_method_to_route(cls, func_name, route_data, app=current_app,
                            *class_args, **class_kwargs):

        rule, route_data = route_data

        if not route_data.get('endpoint'):
            route_data['endpoint'] = str("{0}:{1}".format(cls.__name__,
                                                          func_name))

        proxy = app.view_functions.get(route_data['endpoint'])
        if not proxy:
            def proxy(*args, **kwargs):
                kwargs['__func'] = func_name
                return cls(*class_args,
                           **class_kwargs).dispatch_request(*args, **kwargs)

            if cls.decorators:
                for decorator in cls.decorators:
                    proxy = decorator(proxy)

        cls.add_route(app, rule, proxy, **route_data)

    @classmethod
    def add_route(cls, app, rule, view_func, **kwargs):
        route_base = cls.route_base or ''
        base_url = app.config.get('APPLICATION_ROOT', '/') or '/'
        uri = "{app_root}/{route_base}{route}".format(app_root=base_url,
                                                      route_base=route_base,
                                                      route=rule)
        app.add_url_rule(reduce_slashes(uri), view_func=view_func, **kwargs)


class Controller(MethodView, ControllerRoute):

    route_base = None

    class Response(object):

        @staticmethod
        def to_json(data, status=200, **kwargs):
            return JsonResponse(data, status=status, **kwargs)

        @staticmethod
        def to_xml(data, status=200, **kwargs):
            return XmlResponse(data, status=status, **kwargs)

        @staticmethod
        def to_plain(data, status=200, **kwargs):
            return PlainResponse(data, status=status, **kwargs)

        @staticmethod
        def as_requested(data, status=200, **kwargs):
            accept_header = request.headers.get('content-type') or \
                            request.headers.get('accept').split(',')[0]

            if 'json' in accept_header:
                return Controller.Response.to_json(data, status, **kwargs)
            if 'xml' in accept_header:
                return Controller.Response.to_xml(data, status, **kwargs)
            if 'plain' in accept_header:
                return Controller.Response.as_plain(data, status, **kwargs)

            return make_response(Response(data), status=status, **kwargs)

    @property
    def response(self):
        return Controller.Response

    def __dummy(self, *args, **kwargs):
        pass

    def dispatch_request(self, *args, **kwargs):

        func = kwargs.pop('__func', None)
        if func and not request.is_xhr:
            func = getattr(self, func)
        else:
            func = getattr(self, request.method.lower(), None)
            if func is None and request.method == 'HEAD':
                func = getattr(self, 'get', None)
            if not func:
                raise HTTPNotImplemented()

        action = func.__name__
        getattr(self, "before_{0}".format(action), self.__dummy)(*args, **kwargs)
        result = func(*args, **kwargs)
        getattr(self, "after_{0}".format(action), self.__dummy)(*args, **kwargs)

        if not result:
            result = Response('')

        if isinstance(result, Response):
            return result

        if not isinstance(result, (list, set, tuple)):
            return self.response.as_requested(result)
        # result (data, code) in function e.g. return {}, 300
        return self.response.as_requested(*result)

    def render_view(self, name, view_data, status=200, *args, **kwargs):
        parts = re.split(r'([A-Z][a-z]+)+', self.__class__.__name__)
        parts = map(lambda x: x.lower(), filter(None, parts))
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
