#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import os
import uuid
import json
from flod_common.session.utils import unsign_auth_token
from flask import g

"""
Logging of HTTP requests and responses for Flask App

"""


def assert_config_file_exists(log_config_file):
    if not os.path.isfile(log_config_file):
        raise AssertionError("Could not find configuration file for http logger ('%s' does not exist or is not a file)" % log_config_file)


def setup_http_logger(app, log_config_file):
    """

    :param app: the instance of the flask app for the application where logging is to be done
    :param log_config_file: which log file to load to configure logging. Must be in root of the app that is running, or
    absolute path
    """
    try:
        assert_config_file_exists(log_config_file)
        logging.config.fileConfig(log_config_file, disable_existing_loggers=False)
        app.http_logger = logging.getLogger("http_request")
    except Exception as e:
        app.logger.error('Failed to configure http_logger with config from file \'%s\', \n%s' % (log_config_file, e.message))
        raise

    
def http_request_logger(app, appName, request):
    """

    :param app: the instance of the flask app for the application where logging is to be done
    :param appName: the custom name of the app that is doing the logging to easily identify it in the log if it shares
    log file with other apps
    :param request: the Flask request
    """
    try:
        request_data = ''
        user_info = None
        g.response_sent = False
        if request.method != 'GET':

            if len(request.files) > 0:
                for key, value in request.files.iteritems():
                    request_data += " File: " + str(key) + ":" + str(value) + "|"

            if len(request.form) > 0:
                for key, value in request.form.iteritems():
                    request_data += " " + str(key) + ":" + str(value) + "|"

            if len(request.args) > 0:
                for key, value in request.args.iteritems():
                    request_data += " " + str(key) + ":" + str(value) + "|"

            if request.json:
                request_data += str(json.dumps(request.json))

            if request.cookies:
                if 'auth_token' in request.cookies:
                    user_info = " " + str(unsign_auth_token(request.cookies['auth_token']))

                if not user_info:
                    user_info = "ANONYMOUS USER"

            g.uuid = uuid.uuid4()

            app.http_logger.debug("%s HTTP_AUDIT:REQUEST %s %s %s %s %s" % (appName, g.uuid, user_info, request.method,
                                                                 request.url, request_data))

    except Exception as e:
        # Avoid that we get exception in request due to logging, and that it breaks the web app
        try:
            app.http_logger.exception("%s HTTP_AUDIT:REQUEST LOG ERROR. An exception occured when attempting to log request." %
                                      appName)
        except Exception:
            pass


def http_response_logger(app, appName, request, response=None):
    """
    NOTE: This is not called if there is an unhandled exception! but in that case the user should not get a response..

    :param app: the instance of the flask app for the application where logging is to be done
    :param appName: the custom name of the app that is doing the logging to easily identify it in the log if it shares
    log file with other apps
    :param request: the Flask request
    :param response: the Flask response
    """
    try:

        if request.method != 'GET':
            app.http_logger.debug("%s HTTP_AUDIT:RESPONSE %s %s %s" % (appName, g.uuid, response.status,
                                                            str(json.dumps(response.get_data(as_text=True)))))

        g.response_sent = True
    except Exception as e:
        # Avoid that we get exception in request due to logging, and that it breaks the web app
        try:
            app.http_logger.exception("%s HTTP_AUDIT:RESPONSE LOG ERROR. An exception occured when attempting to log response."
                                      % appName)
        except Exception:
            pass


def http_teardown(app, appName, arg):
    """
    In case there is no response, then we provide this message to inform what happened.

    :param app: the instance of the flask app for the application where logging is to be done
    :param appName: the custom name of the app that is doing the logging to easily identify it in the log if it shares
    log file with other apps
    :param arg: Possibly informative message about what went wrong.
    """
    try:
        if hasattr(app, 'http_logger'):
            if not hasattr(g, 'response_sent') or g.response_sent is False:
                    app.http_logger.debug("%s HTTP_AUDIT:NO RESPONSE %s %s"
                                          % (appName, "No response was sent due to internal exception: ",  str(arg)))
    except Exception as e:
        try:
            app.http_logger.exception("%s HTTP_AUDIT:ERROR TEARDOWN LOG. An exception occured when attempting to log teardown."
                                      % appName)
        except Exception:
            pass