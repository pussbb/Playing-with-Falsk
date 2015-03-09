# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function

import sys

if sys.version_info[0] < 3:
    import imp
    imp.reload(sys)
    sys.setdefaultencoding("UTF-8")

from flask_app import serve

if __name__ == "__main__":
    serve()