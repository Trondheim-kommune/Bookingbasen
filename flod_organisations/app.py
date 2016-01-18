#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import StreamHandler

from flask import Flask

from database import init_db
from api import create_api


API_VERSION = "v1"
DEFAULT_DATABASE_URL = 'sqlite:////tmp/flod_organisations.db'


def create_app(db_url):
    """This is a test

    :param db_url: connection url to the database being used
    :returns: the initialized and created app instance
    """
    app = Flask(__name__)
    (app.db_session, app.db_metadata, app.db_engine) = init_db(db_url)

    @app.teardown_request
    def shutdown_session(exception=None):
        app.db_session.remove()

    create_api(app, API_VERSION)

    # support for remote debugging in Intellij and pycharm
    #
    # Set IDEA_ORGANISATIONS_REMOTE_DEBUG_ON to True in your environment
    # prior to starting the application to get remote debugging.
    #
    # Set IDEA_REMOTE_DEBUG_SERVER to the ip/hostname of the machine running the
    # debug server.
    #
    # Set IDEA_ORGANISATIONS_REMOTE_DEBUG_SERVER to the port of the debug server prosess
    #
    # For the remote debugging to work you will also have to make sure
    # the pycharm-debug.egg is on your path (check your environment file).
    if os.environ.get('IDEA_ORGANISATIONS_REMOTE_DEBUG_ON') == 'True':
        server = os.environ.get('IDEA_REMOTE_DEBUG_SERVER')
        port = os.environ.get('IDEA_ORGANISATIONS_REMOTE_DEBUG_PORT')
        app.logger.info("Idea remote debugging is on! Will connect to debug server running on %s:%s" % (server, port))
        import pydevd
        pydevd.settrace(server, port=int(port), stdoutToServer=True, stderrToServer=True)

    return app


app = create_app(os.environ.get('ORGANISATIONS_DATABASE_URL',
                                DEFAULT_DATABASE_URL))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 1338))
    app = create_app(os.environ.get('ORGANISATIONS_DATABASE_URL',
                                    DEFAULT_DATABASE_URL))

    app.run(host='0.0.0.0', port=port, debug=True)

if not app.debug:
    stream_handler = StreamHandler()
    app.logger.addHandler(stream_handler)
