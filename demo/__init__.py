# -*- coding: utf-8 -*-
"""

"""

from __future__ import unicode_literals, print_function, absolute_import, \
    division

from flask_bootstrap3 import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import flask_app
from flask_app.helpers.app import simple_exception_handler, to_json

APP = flask_app.create_app(flask_app.from_module_name(__name__))
DB = SQLAlchemy(APP)

Bootstrap(APP)
with APP.app_context():
    from . import routes

from .models.user import User, UserSettings

"""
DB.create_all()
DB.session.add(User(username='admin', email='admin@example.com'))
DB.session.add(User(username='user', email='user@example.com'))
DB.session.add(UserSettings(user_id=1, properties='[]'))
DB.session.commit()
user = User.find(username='admin')
iuser = iter(user)
print('iuser', iuser.next())
for column in user:
    print(column)
print('type', type(user.items()))
for column, value in user.items():
    print(column, value)
print(User.find(1).settings)

print('dump', to_json(user))
print('username' in User.find(username='admin'))
print(User.find(1).settings)
"""

def serve(app_env=None):
    flask_app.serve(APP, app_env)

@APP.errorhandler(Exception)
def handler(*args, **kwargs):
    return simple_exception_handler(*args, **kwargs)
