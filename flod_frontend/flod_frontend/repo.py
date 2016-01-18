#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import json
import requests
from flask import request
from flod_common.session.utils import make_auth_cookie

BOOKING_URL = os.environ.get('BOOKING_URL', 'http://localhost:1337')
MATRIKKEL_URL = os.environ.get('MATRIKKEL_URL', 'http://localhost:5500')
USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')
ORGANISATIONS_URL = os.environ.get('ORGANISATIONS_URL',
                                   'http://localhost:1338')
FACILITIES_URL = os.environ.get('FACILITIES_URL', 'http://localhost:5000')


def generate_cookies(auth_token_username):
    if not auth_token_username:
        return {}
    return dict(
        request.cookies.items() +
        make_auth_cookie(auth_token_username).items()
    )

def get_settings(auth_token_username=None):
    url = '{url}/api/v1/adm_leieform'.format(url=BOOKING_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()

def get_applications(person_uri=None, auth_token_username=None):
    url = '{url}/api/v1/applications/'.format(url=BOOKING_URL)
    if person_uri:
        url += "?person_uri=" + person_uri
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_application(application_id, auth_token_username=None):
    url = '{url}/api/v1/applications/{id}'.format(url=BOOKING_URL,
                                                  id=application_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_auto_approve_resources(auth_token_username=None):
    url = '{url}/api/v1/resources/'.format(url=BOOKING_URL)
    params = dict(booking_type='auto_approval_allowed')
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_facilities(auth_token_username=None, params=None):
    url = '{url}/api/v1/facilities/'.format(url=FACILITIES_URL)    
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_facility(facility_id, auth_token_username=None):
    url = '{url}/api/v1/facilities/{id}'.format(url=FACILITIES_URL,
                                                id=facility_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_facility_types():
    url = '{url}/api/v1/facility_types/'.format(url=FACILITIES_URL)
    r = requests.get(url)
    return r.json()


def get_facilities_by_type(facility_type, auth_token_username=None):
    url = '{url}/api/v1/facilities/'.format(url=FACILITIES_URL)
    params = dict(type=facility_type)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()


def get_unit_types(auth_token_username=None):
    url = '{url}//api/v1/unit_types/'.format(url=FACILITIES_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()


def get_districts():
    url = '{url}//api/v1/districts/'.format(url=FACILITIES_URL)
    r = requests.get(url)
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


def get_persons(person_id=None, person_ids=None, auth_token_username=None):
    url = '{url}/api/v1/persons/{person_id}'.format(url=ORGANISATIONS_URL, person_id=person_id if person_id is not None else "")
    params = None
    if person_ids:
        params={
            'person_ids': person_ids
        }

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    r = requests.get(url, data=json.dumps(params), cookies=generate_cookies(auth_token_username), headers=headers)

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


def get_all_organisations(filter, auth_token_username):
    url = '{url}/api/v1/organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username),
                     params=filter)
    return r.json()

def get_resource(facility_id, auth_token_username=None):
    url = '{url}/api/v1/resources/facilities/{id}'.format(url=BOOKING_URL, id=facility_id)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()

def get_all_umbrella_organisations(auth_token_username=None):
    url = '{url}/api/v1/umbrella_organisations/'.format(url=ORGANISATIONS_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
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

def get_bookings_for_date(resource_uri, date):
    url = '{url}/api/v1/slots/'.format(url=BOOKING_URL)
    params = {
        "resource_uri": resource_uri,
        "day": date,
        "status": "Granted"
    }
    r = requests.get(url, params = params)
    return r.json()
    
def get_all_facilities(auth_token_username=None,params=None):
    url = '{url}/api/v1/facilities/'.format(url=FACILITIES_URL)
    r = requests.get(url, cookies=generate_cookies(auth_token_username), params=params)
    return r.json()

def get_umbrella_org_member_organisations(umbrella_organisation_id, auth_token_username=None):
    url = '{url}/api/v1/umbrella_organisations/{id}/organisations'.format(
        url=ORGANISATIONS_URL,
        id=umbrella_organisation_id
    )
    r = requests.get(url, cookies=generate_cookies(auth_token_username))
    return r.json()
