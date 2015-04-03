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


def http_method_route(rule, **kwargs):
    return __real_wrapper('_http_method_route', rule, **kwargs)


class ControllerResponse(Response):

    def __new__(cls, *args, **kwargs):
        kwargs.pop('mimetype', None)
        kwargs.pop('content_type', None)
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

class JsonResponce(ControllerResponse):

    default_mimetype = 'application/json'

    def __init__(self, data, *args, **kwargs):
        super(JsonResponce, self).__init__(json.dumps(data, indent=2),
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

    def dispatch_request(self, *args, **kwargs):
        response = None

        if kwargs.get('__func') and not request.is_xhr:
            func = kwargs.get('__func')
            del kwargs['__func']
            response = getattr(self, func)(*args, **kwargs)
        else:
            try:
                response = super(Controller, self).dispatch_request(*args,
                                                                    **kwargs)
            except AssertionError as exception:
                raise HTTPNotImplemented(exception)

        if isinstance(response, Response):
            return response

        if not isinstance(response, (list, set, tuple)):
            response = [response, 200]

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
        return make_response(*args, **kwargs)

    def json_response(self, data, status=200, *args, **kwargs):
        ''' Return application/json

        '''
        return JsonResponce(data, status=status, *args, **kwargs)

    def xml_response(self, data, status=200, *args, **kwargs):
        ''' Return application/xml

        '''
        return XmlResponse(data, status);

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
