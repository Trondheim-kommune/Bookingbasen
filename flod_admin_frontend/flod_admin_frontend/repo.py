#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import os
import requests
from flask import request, current_app

from flod_common.session.utils import make_auth_cookie

BOOKING_URL = os.environ.get('BOOKING_URL', 'http://localhost:1337')
MATRIKKEL_URL = os.environ.get('MATRIKKEL_URL', 'http://localhost:5500')
USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')
ORGANISATIONS_URL = os.environ.get('ORGANISATIONS_URL', 'http://localhost:1338')
FACILITIES_URL = os.environ.get('FACILITIES_URL', 'http://localhost:5000')


def generate_cookies(auth_token_username):
    return dict(
        request.cookies.items() +
        make_auth_cookie(auth_token_username).items()
    )


def get_all_organisations(organisation_filter, auth_token_username):
    url = '{url}/api/v1/organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username),
                     params=organisation_filter)
    return r.json()


def get_organisations(organisation_ids, organisation_filter, auth_token_username):
    url = '{url}/api/v1/organisations/'.format(url=ORGANISATIONS_URL)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, cookies=generate_cookies(auth_token_username),
                     data=json.dumps({'organisation_ids': organisation_ids}),
                     params=organisation_filter, headers=headers)
    return r.json()


def get_organisation(organisation_id, auth_token_username, params=None):
    url = '{url}/api/v1/organisations/{id}'.format(
        url=ORGANISATIONS_URL,
        id=organisation_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_all_persons(auth_token_username):
    url = '{url}/api/v1/persons/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_persons(person_id=None, person_ids=None, auth_token_username=None):
    url = '{url}/api/v1/persons/{person_id}'.format(url=ORGANISATIONS_URL, person_id=person_id if person_id is not None else "")
    params = None
    if person_ids:
        params = {
            'person_ids': person_ids
        }

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    r = requests.get(url, data=json.dumps(params), cookies=generate_cookies(auth_token_username), headers=headers)

    return r.json()


def get_all_applications(auth_token_username, params=None):
    url = '{url}/api/v1/applications/'.format(url=BOOKING_URL)
    r = requests.get(url, params=params,
                     cookies=generate_cookies(auth_token_username))
    return r.json()


def get_application(application_id, auth_token_username, include_emails=False):
    url = '{url}/api/v1/applications/{id}'.format(
        url=BOOKING_URL,
        id=application_id
    )
    params = {}
    # Request the rendered email template for the application
    if include_emails:
        params["include_emails"] = True
    r = requests.get(url, cookies=generate_cookies(auth_token_username),
                     params=params)
    return r.json()


def get_all_facilities(auth_token_username, params=None):
    url = '{url}/api/v1/facilities/'.format(url=FACILITIES_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_facility(facility_id, auth_token_username):
    url = '{url}/api/v1/facilities/{id}'.format(
        url=FACILITIES_URL,
        id=facility_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_all_facilities_internal_notes(facility_id, auth_token_username):
    url = '%s/api/v1/facilities/%d/notes/' % (FACILITIES_URL, facility_id)
    response = requests.get(url, cookies=generate_cookies(auth_token_username))
    return response.json()


def get_all_facility_types(auth_token_username):
    url = '{url}/api/v1/facility_types/'.format(url=FACILITIES_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_all_unit_types(auth_token_username):
    url = '{url}/api/v1/unit_types/'.format(url=FACILITIES_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_user(user_id, auth_token_username):
    url = '{url}/api/v1/users/{id}'.format(url=USERS_URL, id=user_id)

    r = requests.get(url, cookies=generate_cookies(auth_token_username))
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


def get_rammetid(rammetid_id, auth_token_username=None):
    url = '{url}/api/v1/rammetid/{id}'.format(
        url=BOOKING_URL,
        id=rammetid_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_resources(params, auth_token_username=None):
    url = '{url}/api/v1/resources/'.format(url=BOOKING_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_organisation_statistics(organisation_id, start_date, end_date, auth_token_username=None, params=None):
    url = '{url}/api/v1/organisations/{id}/statistics?start_date={start}&end_date={end}'.format(url=BOOKING_URL, id=organisation_id, start=start_date, end=end_date)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_facility_statistics(facility_id, start_date, end_date, auth_token_username=None):
    url = '{url}/api/v1/facilities/{id}/statistics?start_date={start}&end_date={end}'.format(url=BOOKING_URL, id=facility_id, start=start_date, end=end_date)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_resource(facility_id, auth_token_username=None):
    url = '{url}/api/v1/resources/facilities/{id}'.format(url=BOOKING_URL, id=facility_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_arrangement_conflicts(application_id, auth_token_username):
    url = '{url}/api/v1/arrangement_conflicts/{id}'.format(
        url=BOOKING_URL,
        id=application_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_districts():
    url = '{url}//api/v1/districts/'.format(url=FACILITIES_URL)
    r = requests.get(url)
    return r.json()
