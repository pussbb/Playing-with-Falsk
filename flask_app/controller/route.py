# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from functools import wraps
import inspect
from flask import current_app
from ..helpers.url import app_root_url, reduce_slashes


class ControllerRoute(object):

    @classmethod
    def endpoint(cls, name=""):
        return str("{0}:{1}".format(cls.__name__, name))

    @classmethod
    def register(cls, app=current_app, *class_args, **class_kwargs):
        predict = lambda x: inspect.ismethod(x) or inspect.isfunction(x)

        for func_name, func in inspect.getmembers(cls, predict):
            for item in getattr(func, '_route', []):
                cls.add_method_to_route(func_name, func, item, app, *class_args,
                                        **class_kwargs)

            for item in getattr(func, '_http_method_route', []):
                rule, kwargs = item
                if not kwargs.get('endpoint'):
                    kwargs['endpoint'] = cls.endpoint(func_name.upper())
                kwargs['methods'] = [func_name.upper()]
                view_func = app.view_functions.get(kwargs.get('endpoint')) or \
                            app.view_functions.get(cls.__name__)

                if not view_func:
                    view_func = cls.as_view(cls.__name__, *class_args,
                                            **class_kwargs)

                wraps(func)(view_func)
                cls.add_route(app, rule, view_func, **kwargs)

    @classmethod
    def add_method_to_route(cls, func_name, func, route_data, app=current_app,
                            *class_args, **class_kwargs):

        rule, route_data = route_data
        if not route_data.get('endpoint'):
            route_data['endpoint'] = cls.endpoint(func_name)

        proxy = app.view_functions.get(route_data['endpoint'])
        if not proxy:
            @wraps(func)
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
        route_base = ''
        if cls.resource is None:
            route_base = cls.__name__

        if route_base:
            route_base = route_base[0].lower() + route_base[1:]

        uri = "{app_root}/{route_base}{route}".format(
            app_root=app_root_url(app),
            route_base=route_base,
            route=rule
        )
        # get settings if it an blueprint get it from current app
        config = getattr(app, 'config', current_app.config)
        if 'strict_slashes' not in kwargs.keys():
            kwargs['strict_slashes'] = config.get('STRICT_SLASHES', True)
        app.add_url_rule(reduce_slashes(uri), view_func=view_func, **kwargs)
