# -*- coding: utf-8 -*-
import json
import os

from flask import request
from flask.ext.restful import abort
import requests

from flod_common.session.utils import make_auth_cookie, ADMIN_USER_ID


class ExternalResourceHelper(object):
    org_service_base_url = os.environ.get('ORGANISATIONS_URL', 'http://localhost:1338')
    org_service_version = os.environ.get('ORGANISATIONS_VERSION', 'v1')
    org_root_uri = '%s/api/%s' % (org_service_base_url, org_service_version)

    sak_service_base_url = os.environ.get('SAK_URL', 'http://localhost:1338')
    sak_service_version = os.environ.get('SAK_VERSION', 'v1')
    sak_root_uri = '%s/api/%s' % (sak_service_base_url, sak_service_version)

    user_service_base_url = os.environ.get('USERS_URL', 'http://localhost:4000')
    user_service_version = os.environ.get('USER_VERSION', 'v1')
    user_root_uri = '%s/api/%s' % (user_service_base_url, user_service_version)

    @classmethod
    def post_to_ext(cls, url, filters=None):
        response = requests.post(
            url=url,
            data=json.dumps(filters),
            headers={'content-type': 'application/json; charset=utf-8'},
            cookies=dict(request.cookies.items())
        )

        if response.status_code / 100 != 2:
            abort(response.status_code, __error__=[response.content])
        return response

    @classmethod
    def get_from_ext(cls, url):
        response = requests.get(
            url=url,
            headers={'content-type': 'application/json; charset=utf-8'},
            cookies=dict(request.cookies.items())
        )

        if response.status_code / 100 != 2:
            abort(response.status_code, __error__=[response.content])
        return response

    @classmethod
    def get_organisation_by_name(cls, org_name):
        url = "%s/organisations/?name=%s" % (cls.org_root_uri, org_name)
        response = cls.get_from_ext(url)
        return json.loads(response.content)

    @classmethod
    def get_organisation(cls, id):
        url = cls.org_root_uri + ('/organisations/%s' % id)
        response = cls.get_from_ext(url)
        organisation = json.loads(response.content)
        return organisation

    @classmethod
    def load_organisation(cls, soknad):
        id = soknad['organisation_id']
        if id:
            organisation = cls.get_organisation(id)
            soknad['organisation'] = {}
            soknad['organisation']['name'] = organisation.get('name')
            soknad['organisation']['org_number'] = organisation.get('org_number')
            soknad['organisation']['phone_number'] = organisation.get('phone_number')
            soknad['organisation']['email_address'] = organisation.get('email_address')
            soknad['organisation']['description'] = organisation.get('description')

    @classmethod
    def load_organisations(cls, soknader):
        organisation_ids = list(set([soknad['organisation_id'] for soknad in soknader]))
        if organisation_ids:
            organisations = cls.get_organisations_by_id(organisation_ids)

            for soknad in soknader:
                org_id = soknad['organisation_id']
                if org_id:
                    organisation = next(organisation for organisation in organisations if organisation["id"] == org_id)
                    soknad['organisation'] = {}
                    soknad['organisation']['name'] = organisation['name']

    @classmethod
    def load_users(cls, soknader):
        user_ids = list(set([soknad['saksbehandler_id'] for soknad in soknader]))
        if user_ids:
            users = cls.get_users_by_id(user_ids)

            for soknad in soknader:
                user_id = soknad['saksbehandler_id']
                if user_id:
                    user = next(user for user in users if user["id"] == user_id)
                    soknad['saksbehandler'] = {}
                    soknad['saksbehandler']['name'] = user['profile']['full_name']

    @classmethod
    def load_persons(cls, soknader):
        person_ids = list(set([soknad['person_id'] for soknad in soknader]))
        if person_ids:
            persons = cls.get_persons_by_id(person_ids, auth_token_username=ADMIN_USER_ID)

            for soknad in soknader:
                try:
                    person = next(person for person in persons if person["id"] == soknad["person_id"])
                    soknad['person'] = {'name': "%s %s" % (person['first_name'], person['last_name'])}
                except StopIteration:
                    pass

    @classmethod
    def get_all_persons_in_organisations(cls, org_ids):
        persons_dict = {}
        for org_id in org_ids:
            url = cls.org_root_uri + '/organisations/%s/persons/' % org_id
            response = cls.get_from_ext(url)
            persons = json.loads(response.content)
            for person in persons:
                persons_dict[person['id']] = person
        return persons_dict

    @classmethod
    def get_persons_by_id(cls, person_ids, auth_token_username=None):
        url = '{url}/persons/'.format(url=cls.org_root_uri)
        data = None
        if person_ids:
            data = {
                'person_ids': person_ids
            }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.get(url, data=json.dumps(data), cookies=cls.generate_cookies(auth_token_username), headers=headers)

        return r.json()

    @staticmethod
    def generate_cookies(auth_token_username):
        if not auth_token_username:
            return {}
        return dict(
            request.cookies.items() +
            make_auth_cookie(auth_token_username).items()
        )

    @classmethod
    def get_organisations_by_id(cls, organisation_ids):
        url = '{url}/organisations/'.format(url=cls.org_root_uri)
        data = None
        if organisation_ids:
            data = {
                'organisation_ids': organisation_ids
            }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.get(url, data=json.dumps(data), cookies=request.cookies, headers=headers)
        return r.json()

    @classmethod
    def get_users_by_id(cls, user_ids):
        url = cls.user_root_uri + '/users/public'
        data = None
        if user_ids:
            data = {
                'user_ids': user_ids
            }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.get(url, data=json.dumps(data), cookies=request.cookies, headers=headers)
        return r.json()
