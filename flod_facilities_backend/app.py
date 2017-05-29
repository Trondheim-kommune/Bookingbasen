#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import StreamHandler, INFO

from flask import Flask
from flask.ext.mail import Message, Mail

from api import create_api
from database import init_db

API_VERSION = "v1"

def check_environment(app):
    file_backend = os.environ.get('FILE_BACKEND', 'file').lower()

    if 'FILE_BACKEND' not in os.environ:
        app.logger.info('FILE_BACKEND is not set, will default to "%s"',
                        file_backend)
    if file_backend == 's3':
        if 'S3_BUCKET' not in os.environ:
            app.logger.warn('S3_BUCKET is not set, will default to "flod"')
        if 'AWS_ACCESS_KEY_ID' not in os.environ:
            raise EnvironmentError(('AWS_ACCESS_KEY_ID must be set for S3 '
                                    'backend'))
        if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
            raise EnvironmentError(('AWS_SECRET_ACCESS_KEY must be set for'
                                    ' S3 backend'))

    if file_backend == 'file' and 'UPLOAD_PATH' not in os.environ:
        app.logger.info('UPLOAD_PATH is not set, will default to /tmp')

    if 'AUTH_TOKEN_SECRET' not in os.environ:
        raise EnvironmentError('AUTH_TOKEN_SECRET must be set')

def create_app(db_url):
    app = Flask(__name__)
    (app.db_session, app.db_metadata, app.db_engine) = init_db(db_url)

    @app.teardown_request
    def shutdown_session(exception=None):
        app.db_session.remove()

    create_api(app, API_VERSION)
    if not app.debug:
        stream_handler = StreamHandler()
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(INFO)

    check_environment(app)

    return app


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app = create_app(os.environ.get('DATABASE_URL'))
    app.run(host='0.0.0.0', port=port, debug=True)
