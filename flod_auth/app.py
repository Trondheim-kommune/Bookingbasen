#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import StreamHandler, INFO
import copy
from datetime import timedelta

from flask import Flask

from api.api_bootstrap import create_api
from database import init_db
import default_settings


CFG_HOSTNAME = 'HOSTNAME'
CFG_PORT = 'PORT'
CFG_DATABASE_URL = 'AUTH_DATABASE_URL'
CFG_API_VERSION = 'API_VERSION'
CFG_APP_NAME = 'APP_NAME'
CFG_AUTH_TOKEN_TIMEOUT = 'AUTH_TOKEN_TIMEOUT'
CFG_FLASK_DEBUG = 'DEBUG'

# _http://flask-basicauth.readthedocs.org/en/latest/

def configure_logger(app):
    if app.config.get(CFG_FLASK_DEBUG, None):
        app.debugOn = (True == bool(app.config[CFG_FLASK_DEBUG]))
    # If the application is not in debug the log statements are by default ignored, we fix it by adding a StreamHandler
    if not app.debug:
        stream_handler = StreamHandler()
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(INFO)
    app.logger.info('Logger configured.')


def configure_app(app):
    # loading default module config
    app.config.from_object(default_settings)
    # loading eventual configuration file
    app.config.from_envvar('FLOD_AUTH_APPLICATION_SETTINGS', silent=True)
    # and finally loading some relevant env variables as a last override.
    database_url = os.environ.get(CFG_DATABASE_URL, None)
    host = os.environ.get(CFG_HOSTNAME, None)
    port = os.environ.get(CFG_PORT, None)
    flask_debug = os.environ.get(CFG_FLASK_DEBUG, None)

    if database_url:
        app.config[CFG_DATABASE_URL] = database_url
    if host:
        app.config[CFG_HOSTNAME] = host
    if port:
        app.config[CFG_PORT] = port
    if flask_debug:
        app.config[CFG_FLASK_DEBUG] = flask_debug.lower()


def copy_and_filter_incompatible_type(a_dictionnary):
    copy_of_dict = copy.copy(a_dictionnary)
    for x in copy_of_dict.keys():
        if isinstance(copy_of_dict[x], timedelta):
            del copy_of_dict[x]


def create_app():
    app = Flask(__name__)
    configure_app(app)
    configure_logger(app)

    app.logger.info('Application starting, current configuration is %s', app.config)

    (app.db_session, app.db_metadata, app.db_engine) = init_db(app.config[CFG_DATABASE_URL])

    @app.teardown_request
    def shutdown_session(exception=None):
        app.db_session.remove()

    create_api(app, app.config[CFG_API_VERSION])

    # support for remote debugging in Intellij and pycharm
    #
    # Set IDEA_AUTH_REMOTE_DEBUG_ON to True in your environment
    # prior to starting the application to get remote debugging.
    #
    # Set IDEA_REMOTE_DEBUG_SERVER to the ip/hostname of the machine running the
    # debug server.
    #
    # Set IDEA_AUTH_REMOTE_DEBUG_PORT to the port of the debug server prosess
    #
    # For the remote debugging to work you will also have to make sure
    # the pycharm-debug.egg is on your path (check your environment file).
    if os.environ.get('IDEA_AUTH_REMOTE_DEBUG_ON') == 'True':
        server = os.environ.get('IDEA_REMOTE_DEBUG_SERVER')
        port = os.environ.get('IDEA_AUTH_REMOTE_DEBUG_PORT')
        app.logger.info("Idea remote debugging is on! Will connect to debug server running on %s:%s" % (server, port))
        import pydevd
        pydevd.settrace(server, port=int(port), stdoutToServer = True, stderrToServer = True)

    app.logger.info('Application started.')

    return app


def start_app():
    app = create_app()

    if __name__ == "__main__":
        app.logger.info('Starting %s on %s:%d, debug is %s',
                        app.config[CFG_APP_NAME],
                        app.config[CFG_HOSTNAME],
                        app.config[CFG_PORT],
                        'on' if app.debug else 'off')
        app.run(host=app.config[CFG_HOSTNAME], port=int(app.config[CFG_PORT]), debug=True)

    return app


app = start_app()