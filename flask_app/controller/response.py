# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask import Response, request, make_response, json
from simplexml import dumps as xml_dumps

from ..model import BaseModel


def to_json(data, **kwargs):
    def default(obj):
        if isinstance(obj, BaseModel):
            return obj.dump()
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(obj)
    kwargs['indent'] = 2
    kwargs['default'] = default
    return json.dumps(data, **kwargs)


class CustomResponse(Response):
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
        return super(CustomResponse, self).__init__(response, **kwargs)

    @property
    def data_filters(self):
        return self._data_filters[:]


def wrap_with_root_element(data):
    return {"root": data}


class XmlResponse(CustomResponse):
    _mimetype = 'text/xml'
    _content_type = 'text/xml'
    _data_filters = [wrap_with_root_element, xml_dumps]


class PlainResponse(CustomResponse):
    pass


class JsonResponse(CustomResponse):
    _mimetype = 'application/json'
    _content_type = 'application/json'
    _data_filters = [to_json]


class ControllerResponse(object):

    """ values 'json', 'xml', 'plain'

    """
    DEFAULT_RESPONSE_TYPE = None

    class Response(object):

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
        def empty(status=204, **kwargs):
            return Response(u"", status=status, **kwargs)

        @staticmethod
        def as_requested(data, status=200, **kwargs):
            """ Tries to determine what format is requested by parsing
            request headers 'accept' or 'content-type'

            :param data:
            :param status:
            :param kwargs:
            :return:
            """
            accept_header = request.headers.get('content-type') or \
                            request.headers.get('accept').split(',')[0]

            if 'json' in accept_header:
                return ControllerResponse.Response.to_json(data, status,
                                                           **kwargs)
            if 'xml' in accept_header:
                return ControllerResponse.Response.to_xml(data, status,
                                                          **kwargs)
            if 'plain' in accept_header:
                return ControllerResponse.Response.to_plain(data, status,
                                                            **kwargs)

            return make_response(Response(data), status, **kwargs)

    @property
    def response(self):
        return ControllerResponse.Response

    def make_response(self, *args, **kwargs):
        func = {
            'json': self.response.to_json,
            'xml': self.response.to_xml,
            'plain': self.response.to_plain
        }.get(self.DEFAULT_RESPONSE_TYPE, self.response.as_requested)
        return func(*args, **kwargs)

