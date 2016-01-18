# -*- coding: utf-8 -*-
import os

import requests
from flask import request, abort

from flod_admin_frontend import app


service_base_url = os.environ.get('MATRIKKEL_URL', 'http://localhost:5500')
service_version = os.environ.get('MATRIKKEL_VERSION', 'v1')
addresses_uri = '%s/api/%s/addresses' % (service_base_url, service_version)
buildings_uri = '%s/api/%s/buildings' % (service_base_url, service_version)

matrikkel_user = os.environ["FLOD_MATRIKKEL_USER"]
matrikkel_pass = os.environ["FLOD_MATRIKKEL_PASS"]


def get_data(url, query_string):
    if query_string:
        url = url + "?" + query_string

    response = requests.get(
        url=url,
        auth=(matrikkel_user, matrikkel_pass)
    )

    if response.status_code / 100 != 2:
        abort(404)

    return response.content


@app.route('/api/matrikkel/v1/addresses')
def get_addresses():
    return get_data(addresses_uri, request.query_string)


@app.route('/api/matrikkel/v1/buildings')
def get_buildings():
    return get_data(buildings_uri, request.query_string)
