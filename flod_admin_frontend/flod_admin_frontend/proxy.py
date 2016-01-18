#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import os
from flask import request, current_app
import requests
from flod_common.session.utils import make_auth_cookie, ADMIN_USER_ID


class HttpError(Exception):
    pass


class ResourceProxy(object):
    def post(self, url, data=None, headers=None, files=None, auth_token_username=None, catch_errors=True):
        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.post(
            url=url,
            data=json.dumps(data) if data else None,
            files=files,
            cookies=dict(request.cookies.items() + auth_token_cookies.items()),
            headers=headers if headers else {'content-type': 'application/json'}
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def put(self, url, data=None, headers=None, auth_token_username=None, catch_errors=True):
        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.put(
            url=url,
            data=json.dumps(data) if data else None,
            cookies=dict(request.cookies.items() + auth_token_cookies.items()),
            headers=headers if headers else {'content-type': 'application/json'}
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def delete(self, url, data=None, headers=None, auth_token_username=None, catch_errors=True):
        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.delete(
            url=url,
            data=json.dumps(data) if data else None,
            cookies=dict(request.cookies.items() + auth_token_cookies.items()),
            headers=headers if headers else {'content-type': 'application/json'}
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def get(self, url, query_string=None, auth_token_username=None, catch_errors=True):
        if query_string:
            url = url + "?" + query_string
        auth_token_cookie = make_auth_cookie(auth_token_username)

        response = requests.get(
            url=url,
            cookies=dict(request.cookies.items() + auth_token_cookie.items())
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def cmd_to_url(self, cmd):
        """Returns the correct url for the given command string, supposed to be implemented in subclasses"""
        raise NotImplementedError('%s is not implemented for %s' % (ResourceProxy.cmd_to_url.__name__, self.__class__))


class UserServiceProxy(ResourceProxy):
    service_base_url = os.environ.get('USERS_URL', 'http://localhost:4000')
    service_version = os.environ.get('USERS_VERSION', 'v1')
    users_uri = '%s/api/%s/users' % (service_base_url, service_version)
    credentials_uri = '%s/api/%s/credentials' % (service_base_url, service_version)

    # Gui command names
    cmd_users = 'v1/users'
    cmd_add_edit_facility_credential = 'v1/add_edit_facility_credential'

    def get_user(self, user_id, auth_token_username=None):
        response = self.get(
            '%s/%s' % (self.users_uri, user_id),
            auth_token_username=auth_token_username
        )
        try:
            return json.loads(response.content)
        except:
            return None

    def get_user_by_private_id(self, private_id, auth_token_username=None):
        response = self.get(
            '%s/' % self.users_uri, 'private_id=%s' % private_id,
            auth_token_username=auth_token_username
        )
        try:
            return json.loads(response.content)
        except:
            return None

    def create_or_update_user(self, private_id, auth_token_username=ADMIN_USER_ID):
        return json.loads(
            self.post(
                '%s/' % self.users_uri,
                {'private_id': private_id, 'authentication_type': 'active_directory'},
                auth_token_username=auth_token_username
            ).content
        )

    def add_edit_facility_credential(self, ad_bruker_ident, facility_id, auth_token_username=None):
        user = self.get_user_by_private_id(
            ad_bruker_ident,
            auth_token_username=auth_token_username
        )
        # create credential
        credential_data = self.create_can_edit_facility_credential_for(
            facility_id,
            auth_token_username=auth_token_username
        )
        # add credential for facility
        response = self.add_credential_to_user(
            user,
            credential_data,
            auth_token_username=auth_token_username
        )
        return response

    def can_edit_facility(self, user_id, facility_id, auth_token_username=None):
        user = self.get_user(user_id, auth_token_username=auth_token_username)
        for credential in user['credentials']:
            if credential['id'].startswith('CAN_EDIT_FACILITY') and credential['resource_id'] == str(facility_id):
                return True
        return False

    def create_can_edit_facility_credential_for(self, facility_id, auth_token_username=None):
        credential_id = 'CAN_EDIT_FACILITY' + '_' + str(facility_id)
        credential_description = u'User can modify facility'
        credential_resource_id = facility_id

        data = {
            'description': credential_description,
            'resource_id': credential_resource_id
        }
        return json.loads(
            self.post(
                url='%s/%s' % (self.credentials_uri, credential_id),
                data=data,
                auth_token_username=auth_token_username
            ).content
        )

    def add_credential_to_user(self, user_data, credential_data, auth_token_username=None):
        response = self.post(url='%s/%s/credentials/%s' % (self.users_uri, user_data['id'], credential_data['id']),
                             auth_token_username=auth_token_username
                             )
        return response

    def update_user(self, user_id, data):
        return json.loads(
            self.post(
                '%s/%s' % (self.users_uri, user_id),
                data,
                auth_token_username=ADMIN_USER_ID
            ).content
        )

    def update_user_profile(self, user_id, data, auth_token_username=None):
        return json.loads(
            self.post(
                '%s/%s/profile' % (self.users_uri, user_id),
                data,
                auth_token_username=auth_token_username
            ).content
        )

    def update_user_roles(self, user_id, roles):
        return json.loads(
            self.post(
                '%s/%s/roles' % (self.users_uri, user_id),
                roles,
                auth_token_username=ADMIN_USER_ID
            ).content
        )

    def cmd_to_url(self, cmd):
        if cmd.startswith(self.cmd_users):
            return self.users_uri + cmd.replace(self.cmd_users, '')


user_service_proxy = UserServiceProxy()

gui_service_name_to_service_proxy = {
    'users': user_service_proxy
}
