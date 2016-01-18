#!/usr/bin/env python
# -*- coding: utf-8 -*-

APP_NAME = 'flod_auth'
API_VERSION = "v1"

HOSTNAME = '0.0.0.0'
PORT = 4000

AUTH_DATABASE_URL = 'sqlite:///flod_auth.db'
FLASK_DEBUG = True

AUTH_ADMIN_USER_ID = 'FlodSuperUser'

AUTH_TOKEN_TIMEOUT = 30
