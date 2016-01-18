#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from flod_aktor_frontend import repo
import os
from flask import request, current_app
import requests
from flod_common.session.utils import make_auth_cookie, ADMIN_USER_ID


class HttpError(Exception):
    pass


class ResourceProxy(object):
    def post(self, url, data, headers=None, auth_token_username=None, catch_errors=True):
        if not headers:
            headers = {'content-type': 'application/json'}
        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.post(
            url=url,
            data=json.dumps(data),
            cookies=dict(request.cookies.items() + auth_token_cookies.items()),
            headers=headers
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def put(self, url, data, headers=None, auth_token_username=None, catch_errors=True):
        if not headers:
            headers = {'content-type': 'application/json'}
        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.put(
            url=url,
            data=json.dumps(data),
            cookies=dict(request.cookies.items() + auth_token_cookies.items()),
            headers=headers
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response

    def get(self, url, query_string=None, auth_token_username=None, catch_errors=True):
        if query_string:
            url = url + "?" + query_string

        auth_token_cookies = make_auth_cookie(auth_token_username)
        response = requests.get(
            url=url,
            cookies=dict(request.cookies.items() + auth_token_cookies.items())
        )
        if response.status_code / 100 != 2 and catch_errors:
            raise HttpError(response.status_code, response.content)

        return response


class UserServiceProxy(ResourceProxy):
    service_base_url = os.environ.get('USERS_URL', 'http://localhost:4000')
    service_version = os.environ.get('USERS_VERSION', 'v1')
    users_uri = '%s/api/%s/users' % (service_base_url, service_version)

    def get_user(self, user_id, auth_token_username=None):
        response = self.get(
            '%s/%s' % (self.users_uri, user_id),
            auth_token_username=auth_token_username
        )
        try:
            return json.loads(response.content)
        except:
            return None

    def create_or_update_user(self, private_id, authentication_type):
        return json.loads(
            self.post(
                '%s/' % self.users_uri,
                {'private_id': private_id, 'authentication_type': authentication_type},
                auth_token_username=ADMIN_USER_ID
            ).content
        )

    def update_user(self, user_id, data):
        return json.loads(
            self.post(
                '%s/%s' % (self.users_uri, user_id),
                data,
                auth_token_username=ADMIN_USER_ID
            ).content
        )

    def update_user_profile(self, user_id, dict, auth_token_username=None):
        return json.loads(
            self.post(
                '%s/%s/profile' % (self.users_uri, user_id),
                dict,
                auth_token_username=auth_token_username
            ).content
        )

    def update_user_roles(self, user_id, roles):
        """
        Make sure that idporten users only get idporten/soker role, rest are not allowed.
        :param user_id:
        :param roles:
        :return:
        """
        return json.loads(
            self.post(
                '%s/%s/roles' % (self.users_uri, user_id),
                roles,
                auth_token_username=ADMIN_USER_ID
            ).content
        )


class OrganisationsServiceProxy(ResourceProxy):
    service_base_url = os.environ.get('ORGANISATIONS_URL', 'http://localhost:1338')
    service_version = os.environ.get('ORGANISATIONS_VERSION', 'v1')
    persons_uri = '%s/api/%s/persons' % (service_base_url, service_version)
    organisations_uri = '%s/api/%s/organisations' % (service_base_url, service_version)
    brreg_enhet_uri = '%s/api/%s/brreg/enhet' % (service_base_url, service_version)
    brreg_search_uri = '%s/api/%s/brreg/search' % (service_base_url, service_version)
    brreg_activity_codes_uri = '%s/api/%s/brreg_activity_codes' % (service_base_url, service_version)
    flod_activity_types_uri = '%s/api/%s/flod_activity_types' % (service_base_url, service_version)

    def get_person(self, person_id, auth_token_username=None):
        response = \
            self.get('%s/%s' % (self.persons_uri, person_id),
                     auth_token_username=auth_token_username
                     )
        try:
            return json.loads(response.content)
        except:
            return None

    def get_organisations_for_person(self, person_id, auth_token_username=None):
        response = \
            self.get('%s/%s/organisations/' % (self.persons_uri, person_id),
                     auth_token_username=auth_token_username
                     )
        try:
            return json.loads(response.content)
        except:
            return None

    def get_organisation(self, organisation_id, auth_token_username=None):
        response = \
            self.get('%s/%s' % (self.organisations_uri, organisation_id),
                     auth_token_username=auth_token_username
                     )
        try:
            return json.loads(response.content)
        except:
            return None

    def get_person_by_national_id_number(self, national_id_number, auth_token_username=None):
        response = self.get(
            '%s/' % self.persons_uri,
            'national_identity_number=%s' % national_id_number,
            auth_token_username=ADMIN_USER_ID
        )
        try:
            person_data = json.loads(response.content)
            return person_data
        except:
            return None

    def create_person(self, national_id_number, auth_token_username=None):
        return json.loads(
            self.post(
                '%s/' % self.persons_uri,
                {"national_identity_number": national_id_number},
                auth_token_username=ADMIN_USER_ID
            ).content
        )

    def get_brreg_activity_codes(self, auth_token_username=None):
        url = '%s/' % self.brreg_activity_codes_uri

        return json.loads(
            self.get(
                url,
                auth_token_username=auth_token_username
            ).content
        )

    def get_flod_activity_types(self, auth_token_username=None):
        url = '%s/' % self.flod_activity_types_uri

        return json.loads(
            self.get(
                url,
                auth_token_username=auth_token_username
            ).content
        )

    def get_members(self, organisation_id, auth_token_username=None):
        response = \
            self.get('%s/%s/persons/' % (self.organisations_uri, organisation_id),
                     auth_token_username=auth_token_username
                     )
        try:
            return json.loads(response.content)
        except:
            return None

    def update_organisations(self, organisations, auth_token_username):
        '''
            Provide a list with organisation dictionaries
            Either "id" or "org_number" must be provided for each organisation,
            in order to identify and get the organisation data
        '''
        updated_organisations = []
        for organisation in organisations:
            organisation_json = repo.get_organisation_by_orgnumber_or_brreg_number(organisation, auth_token_username)
            organisation_dict = json.loads(organisation_json)
            try:
                if organisation_dict:
                    organisation_dict.update(organisation)
                    self.update_organisation(organisation_dict['id'], organisation_dict, auth_token_username)
                    updated_organisations.append(organisation_dict)

            except Exception as e:
                current_app.logger.error("Feil ved oppdatering av organisasjonen: %s Feil: %s", organisation["name"], e)

        return updated_organisations

    def update_organisation(self, organisation_id, data, auth_token_username):
        self.put(
            '%s/%s' % (self.organisations_uri, organisation_id),
            data,
            auth_token_username=auth_token_username
        ).content


user_service_proxy = UserServiceProxy()
organisations_service_proxy = OrganisationsServiceProxy()

gui_service_name_to_service_proxy = {
    'organisations': organisations_service_proxy,
    'users': user_service_proxy
}
