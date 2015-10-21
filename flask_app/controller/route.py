# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from functools import wraps
import inspect
from flask import current_app
from ..helpers.url import app_root_url, reduce_slashes

_VIEW_FUNCTIONS = {}


class ControllerRoute(object):
    """Route registrars

    """

    @classmethod
    def endpoint(cls, name=""):
        """Generates string for endpoint

        :param name:
        :return:
        """
        return str("{0}:{1}".format(cls.__name__, name))

    @classmethod
    def register(cls, app=current_app, *cls_args, **cls_kwargs):
        """ Register class methods as application route

        :param app:
        :param cls_args:
        :param cls_kwargs:
        """
        methods = inspect.getmembers(
            cls,
            lambda x: inspect.ismethod(x) or inspect.isfunction(x)
        )

        for func_name, func in methods:
            for item in getattr(func, '_route', []):
                cls.__add_method_to_route(func, item, app, *cls_args,
                                          **cls_kwargs)

            for item in getattr(func, '_http_method_route', []):
                item[1]['methods'] = [func_name.upper()]
                cls.__add_method_to_route(func, item, app, *cls_args,
                                          **cls_kwargs)

    @classmethod
    def __add_method_to_route(cls, func, route_data, app, *cls_args,
                              **cls_kwargs):
        """Add class method to application route

        :param func_name:
        :param func:
        :param route_data:
        :param app:
        :param cls_args:
        :param cls_kwargs:
        :return:
        """
        rule, route_data = route_data
        if not route_data.get('endpoint'):
            route_data['endpoint'] = cls.endpoint(func.__name__)

        proxy = _VIEW_FUNCTIONS.get(route_data['endpoint'])
        if not proxy:
            @wraps(func)
            def proxy(*args, **kwargs):
                return cls(*cls_args, **cls_kwargs).dispatch_request(
                    func.__name__, *args, **kwargs)

            for decorator in cls.decorators:
                proxy = decorator(proxy)

            _VIEW_FUNCTIONS[route_data['endpoint']] = proxy

        cls.add_route(app, rule, proxy, **route_data)

    @classmethod
    def add_route(cls, app, rule, view_func, **kwargs):
        """

        :param app:
        :param rule:
        :param view_func:
        :param kwargs:
        """
        route_base = cls.resource
        if route_base is None:
            route_base = cls.__name__[0].lower() + cls.__name__[1:]

        uri = "{app_root}/{route_base}{route}".format(
            app_root=app_root_url(app),
            route_base=route_base,
            route=rule
        )
        # get settings if it an blueprint get it from current app
        config = getattr(app, 'config', current_app.config)
        if 'strict_slashes' not in kwargs:
            kwargs['strict_slashes'] = config.get('STRICT_SLASHES', True)
        app.add_url_rule(reduce_slashes(uri), view_func=view_func, **kwargs)
