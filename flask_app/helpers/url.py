# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

import re
from flask import url_for, Blueprint

try:
    from urllib.parse import unquote_plus
except ImportError as _:
    from urllib import unquote_plus


def reduce_slashes(url):
    """Reduce slashes in url

    :param url:
    :return: string
    """
    return re.sub(r'(?<!:)//+', '/', url)


def build_url(endpoint, unquote=False, **kwargs):
    """Generates a URL to the given endpoint

    :param endpoint: string
    :param **kwargs: dict
    :return:
    """
    kwargs['_external'] = True
    url = reduce_slashes(url_for(endpoint, **kwargs))
    # by default url_for encodes query parameters according rfc
    if unquote:
        return unquote_plus(url)
    return url


def app_root_url(app, name=""):
    """Builds url for an application including APPLICATION_ROOT which specified
    in the application config

    :param app:
    :param name:
    :return:
    """
    root_url = '/'
    if not isinstance(app, Blueprint):
        root_url = app.config.get('APPLICATION_ROOT', '/') or '/'
    return reduce_slashes(root_url+"/"+name).rstrip("/")
