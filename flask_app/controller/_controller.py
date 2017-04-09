# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

import os
import re

from flask import request

from werkzeug.datastructures import CombinedMultiDict, MultiDict
from werkzeug.exceptions import NotImplemented as HTTPNotImplemented
from werkzeug.utils import cached_property
from werkzeug.wrappers import BaseResponse

from .route import ControllerRoute
from .response import *


class Controller(ControllerResponse, ControllerRoute):

    decorators = []

    resource = None

    __split_by_capital = re.compile('([A-Z][a-z]+)+')

    @cached_property
    def template_dir(self):
        parts = self.__split_by_capital.split(self.__class__.__name__)
        return os.path.join(*[item.lower() for item in parts])

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


        :param func_name:
        :param args:
        :param kwargs:
        :return: :raise HTTPNotImplemented:
        """
        func = getattr(self, func_name, None)
        if not func:
            raise HTTPNotImplemented()

        self._before(*args, **kwargs)
        action = func.__name__
        getattr(self, 'before_' + action, self.__dummy)(*args, **kwargs)
        result = func(*args, **kwargs)
        getattr(self, 'after_' + action, self.__dummy)(*args, **kwargs)
        self._after(*args, **kwargs)

        if not result:
            result = self.response.empty()

        if isinstance(result, BaseResponse):
            return result

        if not isinstance(result, (list, set, tuple)):
            return self.make_response(result, action=action)

        return self.make_response(*result, action=action)

    @cached_property
    def request_values(self):
        """ Get requested query parameters including all GET and POST

        :return: MultiDict
        """
        json_data = request.get_json()
        if not json_data:
            json_data = []

        args = []
        for d in json_data, request.values:
            if not isinstance(d, MultiDict):
                d = MultiDict(d)
            args.append(d)
        return CombinedMultiDict(args)
