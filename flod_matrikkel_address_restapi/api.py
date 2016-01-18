#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
from flask import request, Response, abort
from flask.ext.basicauth import BasicAuth

from matrikkel import MatrikkelBuildingService, MatrikkelAdressService



MUNICIPALITY_NR = "1601"

def create_api(app, api_version, matrikkel_url, matrikkel_user, matrikkel_pass):

    basic_auth = BasicAuth(app)

    path = os.path.dirname(os.path.realpath(__file__))

    address_service = MatrikkelAdressService(
        '%s/innsynapi_v3/adresse/AdresseWebService?WSDL' % matrikkel_url,
        'file://%s/AdresseWebService.xml' % path,
        matrikkel_user,
        matrikkel_pass
    )

    building_service = MatrikkelBuildingService(
        '%s/innsynapi_v3/bygning/BygningWebService?WSDL' % matrikkel_url,
        'file://%s/BygningWebService.xml' % path,
        matrikkel_user,
        matrikkel_pass
    )

    @app.route("/api/%s/addresses" % api_version)
    @basic_auth.required
    def addresses_api():
        query = request.args.get('query', None)
        if query:
            addresses = address_service.search_address(query, MUNICIPALITY_NR)
            return Response(json.dumps(addresses), mimetype="application/json")
        abort(404)

    @app.route("/api/%s/buildings" % api_version)
    @basic_auth.required
    def buildings_api():
        gardsnr = request.args.get('gardsnr', None)
        bruksnr = request.args.get('bruksnr', None)
        festenr = request.args.get('festenr', None)
        seksjonsnr = request.args.get('seksjonsnr', None)
        if bruksnr and gardsnr:
            buildings = building_service.find_buildings(
                MUNICIPALITY_NR,
                gardsnr,
                bruksnr,
                festenr,
                seksjonsnr
            )
            return Response(json.dumps(buildings), mimetype="application/json")
        abort(404)
