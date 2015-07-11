from distutils.core import setup

setup(
    name='Flask-App',
    version='0.1',
    packages=['flask_app', 'flask_app.helpers', 'flask_app.controller'],
    url='https://github.com/pussbb/Playing-with-Falsk',
    license='',
    author='pussbb',
    author_email='pussbb@gmail.com',
    description='',
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'Flask-SQLAlchemy',
    ],
)
