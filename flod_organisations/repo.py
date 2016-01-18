# -*- coding: utf-8 -*-

import os
import json

import requests
from flod_common.session.utils import unsign_auth_token


USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')
USERS_VERSION = os.environ.get('USERS_VERSION', 'v1')


def is_super_admin(cookies=None):
    if cookies:
        if 'auth_token' in cookies:
            username = unsign_auth_token(cookies['auth_token'])
            super_user_name = os.environ["AUTH_ADMIN_USER_ID"]
            if username == super_user_name:
                return True
    return False


def get_user_id_for_user(cookies=None):
    if cookies:
        if cookies['auth_token']:
            username = unsign_auth_token(cookies['auth_token'])
            super_user_name = os.environ["AUTH_ADMIN_USER_ID"]
            if username != super_user_name:
                return username
    return None


def get_user_by_id(user_id, cookies):
    url = '%s/api/%s/users/%s' % (USERS_URL, USERS_VERSION, user_id)
    response = requests.get(url, cookies=cookies)
    return response.json()


def has_role(user, name):
    return name in (role['name'] for role in user.get('roles', []))


def is_administrator(user):
    return has_role(user, 'flod_brukere') or has_role(user, u'flod_aktørregister_admin') or has_role(user, 'tilskudd_saksbehandler') or has_role(user, 'tilskudd_godkjenner')


def get_user(cookies):
    if 'auth_token' not in cookies:
        return None
    username = unsign_auth_token(cookies['auth_token'])
    url = '%s/api/%s/users/%s' % (USERS_URL, USERS_VERSION, username)
    r = requests.get(url, cookies=cookies)
    return r.json()
