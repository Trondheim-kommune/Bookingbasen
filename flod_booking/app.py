#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import StreamHandler, INFO

from flask import Flask
from flask.ext.bouncer import Bouncer

from database import init_db
from api import create_api
from api.auth import create_bouncer


API_VERSION = "v1"


def create_app(db_url):
    app = Flask(__name__)
    (app.db_session, app.db_metadata, app.db_engine) = init_db(db_url)
    app.debug = os.environ.get('DEBUG') == 'True'

    @app.teardown_request
    def shutdown_session(exception=None):
        app.db_session.remove()

    if not app.debug:
        app.logger.addHandler(StreamHandler())
        app.logger.setLevel(INFO)

    create_api(app, API_VERSION)
    create_bouncer(app)
    return app


app = create_app(os.environ.get('BOOKING_DATABASE_URL', 'sqlite:////tmp/flod_booking.db'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1337))
    app = create_app(os.environ.get('BOOKING_DATABASE_URL', 'sqlite:////tmp/flod_booking.db'))
    app.run(host='0.0.0.0', port=port, debug=True)
