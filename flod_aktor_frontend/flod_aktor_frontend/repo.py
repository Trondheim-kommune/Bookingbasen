#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import os
import requests
from flask import request, current_app
from flod_common.session.utils import make_auth_cookie

USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')
ORGANISATIONS_URL = os.environ.get('ORGANISATIONS_URL', 'http://localhost:1338')


def generate_cookies(auth_token_username):
    if not auth_token_username:
        return {}
    return dict(
        request.cookies.items() +
        make_auth_cookie(auth_token_username).items()
    )


def get_districts():
    url = '{url}/api/v1/districts/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url)
    return r.json()


def get_districts_without_whole_trd():
    districts = get_districts()
    districts_without_whole_trd = [d for d in districts if d["id"] != 0]

    return districts_without_whole_trd


def get_activity_types(auth_token_username=None):
    url = '{url}/api/v1/flod_activity_types/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_organisations():
    url = '{url}/api/v1/organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url)
    return r.json()


def get_organisations_for_person(person_id, auth_token_username):
    url = '{url}/api/v1/persons/{id}/organisations/'.format(
        url=ORGANISATIONS_URL, id=person_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_organisation(organisation_id, auth_token_username=None):
    url = '{url}/api/v1/organisations/{id}'.format(url=ORGANISATIONS_URL,
                                                   id=organisation_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    r.raise_for_status()
    return r.json()


def get_notes(organisation_id, auth_token_username=None):
    url = '{url}/api/v1/organisations/{id}/notes/'.format(url=ORGANISATIONS_URL,
                                                          id=organisation_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    r.raise_for_status()
    return r.json()


def get_persons(auth_token_username=None):
    url = '{url}/api/v1/persons/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_brreg_activity_codes():
    url = '{url}/api/v1/brreg_activity_codes/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url)
    return r.json()


def get_members(organisation_id, auth_token_username=None):
    url = '{url}/api/v1/organisations/{id}/persons/'.format(
        url=ORGANISATIONS_URL, id=organisation_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_user(user_id, auth_token_username=None):
    url = '{url}/api/v1/users/{id}'.format(url=USERS_URL, id=user_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_flod_activity_types():
    url = '{url}/api/v1/flod_activity_types'.format(url=ORGANISATIONS_URL)
    r = requests.get(url)
    return r.json()


def get_all_organisations(filter, auth_token_username):
    url = '{url}/api/v1/organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username),
                     params=filter)
    return r.json()


def get_all_umbrella_organisations(auth_token_username=None, params=None):
    url = '{url}/api/v1/umbrella_organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_umbrella_organisation(umbrella_organisation_id, auth_token_username=None):
    url = '{url}/api/v1/umbrella_organisations/{id}'.format(
        url=ORGANISATIONS_URL,
        id=umbrella_organisation_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_umbrella_organisations_for_person(person_id, auth_token_username=None):
    url = '{url}/api/v1/umbrella_organisations/'.format(url=ORGANISATIONS_URL)
    if person_id:
        url += "?person_id=" + str(person_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_organisation_by_orgnumber_or_brreg_number(data,
                                                  auth_token_username):
    '''
    If the data dict contains "id", the organisation lookup is done with that, otherwise it will
    do lookup with "org_number". The JSON representation of the object/dict is returned.
    If none are specfied, {} is returned.
    If more than one organisation is found (...) {} is returned.
    '''

    organisation_entity = {}

    org_id = data.get("id", None)
    brreg_number = data.get("org_number", None)

    if org_id:
        organisation_entity = get_organisation(org_id, auth_token_username)

    elif brreg_number:
        filter = {"org_number": brreg_number}
        organisation_entities = get_all_organisations(filter=filter,
                                                      auth_token_username=auth_token_username)

        if len(organisation_entities) == 1:
            organisation_entity = organisation_entities[0]
        else:
            current_app.logger.info(
                "%s organisasjoner ble funnet med brreg-nummer %s.",
                len(organisation_entities), brreg_number)
    else:
        current_app.logger.info(
            "Verken organisasjonsnummer eller brreg-nummer er angitt.")

    return json.dumps(organisation_entity)
