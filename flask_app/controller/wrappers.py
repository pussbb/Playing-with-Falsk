# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
from functools import wraps


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


def http_method(rule, **kwargs):
    return __real_wrapper('_http_method_route', rule, **kwargs)
