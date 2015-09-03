# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from functools import wraps

__all__ = ["route", "get_method", "post_method", "delete_method",
           "put_method", "http_method"]


def __real_wrapper(attr, rule, **kwargs):
    def real_wrapper(func):
        """real wrapper

        :param func:
        :return:
        """
        func_attr = getattr(func, attr, [])
        func_attr.append((rule, kwargs))
        setattr(func, attr, func_attr)

        @wraps(func)
        def wrapper(self, *func_args, **func_kwargs):
            """

            :param self:
            :param func_args:
            :param func_kwargs:
            :return:
            """
            return func(self, *func_args, **func_kwargs)

        return wrapper

    return real_wrapper


def route(rule, **kwargs):
    """Decorator to add class method into application routes

    :param rule:
    :param kwargs:
    :return:
    """
    return __real_wrapper('_route', rule, **kwargs)


def get_method(rule, **kwargs):
    """Decorator to add class method into application routes only for HTTP GET
    method.

    :param rule:
    :param kwargs:
    :return:
    """
    kwargs['methods'] = ['GET']
    return route(rule, **kwargs)


def post_method(rule, **kwargs):
    """Decorator to add class method into application routes only for HTTP POST
     method.

    :param rule:
    :param kwargs:
    :return:
    """
    kwargs['methods'] = ['POST']
    return route(rule, **kwargs)


def delete_method(rule, **kwargs):
    """Decorator to add class method into application routes only for HTTP
     DELETE method.

    :param rule:
    :param kwargs:
    :return:
    """
    kwargs['methods'] = ['DELETE']
    return route(rule, **kwargs)


def put_method(rule, **kwargs):
    """Decorator to add class method into application routes only for HTTP
     PUT method.

    :param rule:
    :param kwargs:
    :return:
    """
    kwargs['methods'] = ['PUT']
    return route(rule, **kwargs)


def http_method(rule, **kwargs):
    """Decorator to add class method into application routes where name of the
     function will be HTTP method.

    :param rule:
    :param kwargs:
    :return:
    """
    return __real_wrapper('_http_method_route', rule, **kwargs)
