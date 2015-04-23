# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division
import importlib
import os
import warnings

from flask import current_app

from .controllers import welcome, build


welcome.Welcome.register()
build.Build.register()

__CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
__BLUEPRINTS_FOLDER_NAME = 'blueprints'
__BLUEPRINTS_FOLDER = os.path.join(__CURRENT_DIR, __BLUEPRINTS_FOLDER_NAME)
dir_path, dirs, files = next(os.walk(__BLUEPRINTS_FOLDER))
if '__init__.py' in files:
    base_module = '.'.join([__name__.split('.')[0], __BLUEPRINTS_FOLDER_NAME])
    for dir_name in dirs:
        init_file = os.path.join(dir_path, dir_name, '__init__.py')
        if not os.path.isfile(init_file):
            warnings.warn("Folder {0} is not python module".format(
                os.path.join(dir_path, dir_name))
            )
            continue
        try:
            module = importlib.import_module(
                '.'.join([base_module, dir_name, 'blueprint'])
            )
        except ImportError as _:
            warnings.warn("Module {0} is not blueprint".format(dir_name))
        else:
            module.register_blueprint(current_app)
else:
    warnings.warn("Folder {0} is not python module".format(dir_path))

