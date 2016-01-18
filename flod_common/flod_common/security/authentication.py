#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flod_common.session.utils import unsign_auth_token


def is_idporten_user(user):
    authentication_type = user.get('authentication_type', None)
    return authentication_type and authentication_type == 'id_porten'


def is_active_directory_user(user):
    authentication_type = user.get('authentication_type', None)
    return authentication_type and authentication_type == 'active_directory'


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


def get_user_id_from_cookies(cookies):
    if 'auth_token' not in cookies:
        return None
    return unsign_auth_token(cookies['auth_token'])
