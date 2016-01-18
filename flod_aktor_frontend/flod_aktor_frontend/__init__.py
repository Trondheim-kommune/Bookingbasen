#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import Flask
from webassets.loaders import PythonLoader
from flask.ext.assets import Environment, Bundle


app = Flask(__name__)
app.debug = os.environ.get('DEBUG') == 'True'

assets = Environment(app)
assets.debug = app.debug
bundles = PythonLoader('assetbundle').load_bundles()
for name, bundle in bundles.iteritems():
    assets.register(name, bundle)

from flod_aktor_frontend import views, proxy


def check_environment(app):
    if 'AUTH_TOKEN_SECRET' not in os.environ:
        raise EnvironmentError('Environment variable AUTH_TOKEN_SECRET must be set')


check_environment(app)
