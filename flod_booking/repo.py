#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import requests
from flask import current_app
from flod_common.session.utils import (unsign_auth_token,
                                       verify_superuser_auth_token)

USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')
USERS_VERSION = os.environ.get('USERS_VERSION', 'v1')


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
    return response


def get_user(cookies):
    if 'auth_token' not in cookies:
        current_app.logger.info('auth_token not found in cookies')
        return None
    auth_token = cookies['auth_token']
    username = unsign_auth_token(auth_token)
    if username is None:
        current_app.logger.info(('auth_token could not be '
                                 'unsigned: auth_token=%s'), auth_token)
        return None
    url = '%s/api/%s/users/%s' % (USERS_URL, USERS_VERSION, username)
    r = requests.get(url, cookies=cookies)
    return r.json()


def has_role(user, name):
    return name in (role['name'] for role in user.get('roles', []))


def is_administrator(user):
    return has_role(user, 'flod_brukere')


def make_credential_id(facility_id):
    return 'CAN_EDIT_FACILITY' + '_' + str(facility_id)


def has_edit_credentials(data, facility_id):
    if "credentials" not in data:
        return False

    target_cred = make_credential_id(facility_id)
    for cred in data["credentials"]:
        if cred["id"] == target_cred:
            return True

    return False


def can_user_edit_facility(user_id, facility_id, cookies):
    response = get_user_by_id(user_id, cookies)
    data = response.json()
    return has_edit_credentials(data, facility_id)
