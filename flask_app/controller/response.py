# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

import os

from flask import Response, request, make_response, json, render_template
from flask._compat import string_types

try:
    from flask_sqlalchemy import BaseQuery
except ImportError as _:
    BaseQuery = []
from simplexml import dumps as xml_dumps


__all__ = ['XmlResponse', 'PlainResponse', 'HTMLResponse', 'JsonResponse',
           'ControllerResponse']


def to_json(data, **kwargs):
    """Helper class to dump data from DB.Model(SQLAlchemy) class

    :param data:
    :param kwargs:
    :return:
    """

    def default(obj):
        """wrapper function

        :param obj:
        :return:
        """
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode()

        if obj and hasattr(obj, 'dump'):
            return obj.dump()

        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder().default(obj)

    kwargs['indent'] = 0
    kwargs['default'] = default
    kwargs['ensure_ascii'] = False
    return json.dumps(data, **kwargs)


class CustomResponse(Response):
    """

    :param response:
    :param kwargs:
    """
    _mimetype = 'text/plain'
    _content_type = 'text/plain'
    _data_filters = []

    def __init__(self, response, **kwargs):
        kwargs['mimetype'] = self._mimetype
        kwargs['content_type'] = self._content_type
        headers = kwargs.pop('headers', {})
        if headers:
            headers.pop('Content-Type', None)
            kwargs['headers'] = headers
        for filter_func in self._data_filters:
            response = filter_func(response)
        super(CustomResponse, self).__init__(response, **kwargs)

    @property
    def data_filters(self):
        """List of all data filters of response class

        :return: list
        """
        return self._data_filters[:]


def prepare_data(data):
    """Walk throw data and prepare it for PlainResponse or XMLResponse

    :param data:
    :param add_model_name:
    :return:
    """
    if not data:
        return data

    if hasattr(data, 'dump'):
        return prepare_data({data.__class__.__name__.lower(): data.dump()})
    if isinstance(data, (list, tuple, set, BaseQuery)):
        return [prepare_data(item) for item in data]
    if isinstance(data, dict):
        return {key: prepare_data(value) for key, value in data.items()}
    return data


def wrap_with_root_element(data):
    """Helper function for XmlResponse it wraps data with root element

    :param data:
    :return:
    """
    return {'root': data}


class XmlResponse(CustomResponse):
    """Helper class to send valid plain response with valid response headers
    and prepared data for this format

    """
    _mimetype = 'text/xml'
    _content_type = 'text/xml'
    _data_filters = [prepare_data, wrap_with_root_element, xml_dumps]


class PlainResponse(CustomResponse):
    """Helper class to send valid plain response with valid response headers
    and prepared data for this format

    """
    _mimetype = 'text/plain'
    _content_type = 'text/plain'
    _data_filters = []


class HTMLResponse(CustomResponse):
    """Helper class to send valid html response with valid response headers

    """
    _mimetype = 'text/html'
    _content_type = 'text/html'


class JsonResponse(CustomResponse):
    """Helper class to send valid json response with valid response headers and
    dumped data into JSON data format

    """

    _mimetype = 'application/json'
    _content_type = 'application/json'
    _data_filters = [to_json]


class ControllerResponse(object):
    """ values 'json', 'xml', 'plain'

    """
    DEFAULT_RESPONSE_TYPE = None

    template_dir = None

    class Response(object):
        """Abstract class

        """

        @staticmethod
        def to_json(data, status=200, **kwargs):
            """ Send response in JSON format

            :param data:
            :param status: int
            :param kwargs:
            :return:
            """
            return JsonResponse(data, status=status, **kwargs)

        @staticmethod
        def to_xml(data, status=200, **kwargs):
            """ Send response in XML format

            :param data:
            :param status:
            :param kwargs:
            :return:
            """
            return XmlResponse(data, status=status, **kwargs)

        @staticmethod
        def to_plain(data, status=200, **kwargs):
            """ Send response as plain text

            :param data:
            :param status:
            :param kwargs:
            :return:
            """
            return PlainResponse(data, status=status, **kwargs)

        @staticmethod
        def to_html(data, status=200, **kwargs):
            """ Send response as plain text

            :param data:
            :param status:
            :param kwargs:
            :return:
            """
            return HTMLResponse(data, status=status, **kwargs)

        @staticmethod
        def empty(status=204, **kwargs):
            """Returns empty response with a 204 http status code

            :param status:
            :param kwargs:
            :return:
            """
            return Response(b'', status=status, **kwargs)

        @staticmethod
        def guess_output():
            accept_header = request.headers.get(
                'content-type',
                request.headers.get('accept').split(',')[0]
            )

            func = None
            if 'json' in accept_header:
                func = ControllerResponse.Response.to_json
            elif 'xml' in accept_header:
                func = ControllerResponse.Response.to_xml
            elif 'plain' in accept_header:
                func = ControllerResponse.Response.to_plain
            elif 'html' in accept_header:
                func = ControllerResponse.Response.to_html
            return func

        @staticmethod
        def as_requested(data, status=200, **kwargs):
            """ Tries to determine what format is requested by parsing
            request headers 'accept' or 'content-type'

            :param data:
            :param status:
            :param kwargs:
            :return:
            """
            func = ControllerResponse.Response.guess_output()
            if func:
                return func(data, status, **kwargs)
            return make_response(Response(data), status, **kwargs)

    @property
    def response(self):
        """Return Response class


        :return: class
        """
        return ControllerResponse.Response

    def make_response(self, *args, **kwargs):
        """Sends http response if DEFAULT_RESPONSE_TYPE is set it will
        send response in that format. Otherwise it will try to guess in which
        format response should be based on request header 'content-type'

        :param args:
        :param kwargs:
        :return:
        """
        func = {
            'json': self.response.to_json,
            'xml': self.response.to_xml,
            'plain': self.response.to_plain,
        }.get(self.DEFAULT_RESPONSE_TYPE,
              ControllerResponse.Response.guess_output())
        action = kwargs.pop('action', None)
        if func and 'html' in func.__name__:
            view_name = '/'.join([self.__class__.__name__.lower(), action])
            return self.render_view(view_name + '.html', *args, **kwargs)
        return func(*args, **kwargs)

    def render_view(self, view_name_or_list, view_data, status=200, *args,
                    **kwargs):
        """ Renders view in addition adds controller name in lower case as
        directory where file should be. To disable behavior adding class name
        please use '//' at the beginning of your template name
        for e.g. '//path/some.html' -> 'path/some.html'

        :param name: file name or list of file names for e.g. index.html
        :param view_data: dictionary with data which needed to render view
        :param status: int status code default 200
        :param args:
        :param kwargs:
        :return:
        """

        assert view_name_or_list, "View name must not be empty"

        if isinstance(view_name_or_list, string_types):
            view_name_or_list = [view_name_or_list]
        views = []
        for view_name in view_name_or_list:
            views.append(os.path.join(self.template_dir, view_name))
            views.append(view_name)

        if not isinstance(view_data, dict):
            view_data = {'data': view_data}
        return make_response(
            render_template(views, **view_data),
            status,
            *args,
            **kwargs
        )

    def render_nothing(self):
        """ Will generate valid empty response with 204 http status code

        :return:
        """
        return self.response.empty()
