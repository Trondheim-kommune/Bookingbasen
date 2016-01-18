#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from logging import StreamHandler
from flask import Flask

from api import create_api

API_VERSION = "v1"

def create_app(username, password, matrikkel_url, matrikkel_user, matrikkel_pass):
    app = Flask(__name__)

    app.config['BASIC_AUTH_FORCE'] = True
    app.config['BASIC_AUTH_USERNAME'] = username
    app.config['BASIC_AUTH_PASSWORD'] = password

    create_api(app, API_VERSION, matrikkel_url, matrikkel_user, matrikkel_pass)
    if not app.debug:
        stream_handler = StreamHandler()
        app.logger.addHandler(stream_handler)

    return app


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5500))


    username = os.environ["FLOD_MATRIKKEL_USER"]
    password = os.environ["FLOD_MATRIKKEL_PASS"]

    matrikkel_base_url = os.environ["MATRIKKEL_BASE_URL"]
    matrikkel_user = os.environ["MATRIKKEL_USERNAME"]
    matrikkel_password = os.environ["MATRIKKEL_PASSWORD"]

    app = create_app(
        username,
        password,
        matrikkel_base_url,
        matrikkel_user,
        matrikkel_password
    )
    app.run(host='0.0.0.0', port=port, debug=False)
