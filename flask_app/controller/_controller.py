# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division


import os

from flask import render_template, request, make_response
from werkzeug.exceptions import NotImplemented as HTTPNotImplemented
from flask.views import MethodView

import re
from werkzeug.wrappers import BaseResponse

from .route import ControllerRoute
from .response import *


class Controller(MethodView, ControllerRoute, ControllerResponse):

    resource = None

    def __dummy(self, *args, **kwargs):
        """For internal usage and do nothing

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def _before(self, *args, **kwargs):
        """ Use it when you want to run things before running the class methods

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def _after(self, *args, **kwargs):
        """ Do something before rendering the output.

        :param args:
        :param kwargs:
        :return:
        """
        pass

    def dispatch_request(self, func_name, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: :raise HTTPNotImplemented:
        """
        func = getattr(self, func_name, None)
        if not func:
            raise HTTPNotImplemented()

        self._before(*args, **kwargs)
        action = func.__name__
        getattr(self, "before_{0}".format(action), self.__dummy)(*args,
                                                                 **kwargs)
        result = func(*args, **kwargs)
        getattr(self, "after_{0}".format(action), self.__dummy)(*args, **kwargs)
        self._after(*args, **kwargs)

        if not result:
            result = self.response.empty()

        if isinstance(result, BaseResponse):
            return result

        if not isinstance(result, (list, set, tuple)):
            return self.make_response(result)

        return self.make_response(*result)

    def render_view(self, template_name_or_list, view_data, status=200, *args,
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

        if not template_name_or_list:
            raise ValueError("View name must not be empty")
        if not isinstance(template_name_or_list, (list, tuple, set)):
            template_name_or_list = [template_name_or_list]
        templates = []
        for template_name in template_name_or_list:
            if not template_name.startswith('//'):
                parts = re.split(r'([A-Z][a-z]+)+', self.__class__.__name__)
                parts = map(lambda x: x.lower(), filter(None, parts))
                parts.append(template_name)
                templates.append(os.path.join(*parts))
            else:
                templates.append(template_name.lstrip('//'))

        return make_response(
            render_template(templates, **view_data),
            status,
            *args,
            **kwargs
        )

    def render_nothing(self):
        """ Will generate valid empty response with 204 http status code

        :return:
        """
        return self.response.empty()

    @property
    def request_values(self):
        """ Get requested query parameters including all GET and POST

        :return: MultiDict
        """
        return request.values
