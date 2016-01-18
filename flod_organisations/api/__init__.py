# -*- coding: utf-8 -*-
import os
import json

from flask import current_app, request, Response
from flask.ext.restful import abort, fields, marshal_with, marshal
from sqlalchemy.orm.exc import NoResultFound
from export_report import ExportOgranisationsResource

from domain.models import Address, Organisation, Person, \
    BrregActivityCode, FlodActivityType, UmbrellaOrganisation, \
    PersonOrgAssociationRole, OrganisationPersonAssociation, \
    UmbrellaOrgMemberOrgAssociation, OrganisationInternalNote, District
from flodapi import FlodApi
from flod_common.session.utils import (unsign_auth_token,
                                       verify_auth_token,
                                       verify_superuser_auth_token)

from util.brregclient import BrRegClient, OrgNrNotFoundException
from api import PersonsResource, PersonResource, PersonOrganisationsResource, OrganisationResource, \
    OrganisationPersonsResource, UmbrellaOrganisationResource, UmbrellaOrganisationPersonsResource, \
    UmbrellaOrgMemberOrgAssociationsResource, BrregActivityCodeResource, FlodActivityTypeResource, DistrictResource, \
    OrganisationInternalNotesResource, address_fields

BRREG_URL = os.environ.get("FLOD_BRREG_URL")
BRREG_USER_ID = os.environ.get("FLOD_BRREG_USER")
BRREG_PASSWORD = os.environ.get("FLOD_BRREG_PASS")
USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')

booking_service_base_url = os.environ.get('BOOKING_URL', "http://localhost:1337")
booking_service_version = os.environ.get('BOOKING_VERSION', 'v1')
organisation_booking_uri = '%s/api/%s/organisations' % (booking_service_base_url, booking_service_version)

try:
    brreg_client = BrRegClient(BRREG_URL, BRREG_USER_ID, BRREG_PASSWORD)
except Exception:
    brreg_client = None



brreg_name_search_fields = {
    'name': fields.String(attribute='OrgNavn', default=None),
    'org_number': fields.String(attribute='Orgnr', default=None),
    'org_form': fields.String(attribute='OrgForm', default=None),
    'postal_place': fields.String(attribute='Sted', default=None),
    'is_registered': fields.Boolean,
    'relevance_score': fields.String(attribute='Score', default=None),
    'id': fields.Integer(default=None)
}

brreg_org_fields = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None),
    'org_number': fields.String(default=None),
    'org_form': fields.String(default=None),
    'account_number': fields.String(default=None),

    'email_address': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'telefax_number': fields.String(default=None),
    'url': fields.String(default=None),
    'uri': fields.String(default=None),

    'business_address': fields.Nested(address_fields, allow_null=True),
    'postal_address': fields.Nested(address_fields, allow_null=True),
    'is_public': fields.Boolean,

    # activity codes
    'brreg_activity_code': fields.List(fields.String),

    # Trondheim kommune specific fields
    'flod_activity_type': fields.List(fields.Integer, default=[]),
    'num_members_b20': fields.Integer(default=None),
    'num_members': fields.Integer(default=None),
    'description': fields.String(default=None),
    'area': fields.Integer(default=None),
    'registered_tkn': fields.Boolean,
    'is_registered': fields.Boolean
}


def create_api(app, api_version):
    api = FlodApi(app)

    ##
    ## Actually setup the Api resource routing here
    ##

    api.add_resource(PersonsResource, '/api/%s/persons/' % api_version)

    api.add_resource(
        PersonResource,
        '/api/%s/persons/' % api_version,
        '/api/%s/persons/<int:person_id>' % api_version
    )

    api.add_resource(
        PersonOrganisationsResource,
        '/api/%s/persons/<int:person_id>/organisations/' % api_version
    )

    api.add_resource(
        OrganisationResource,
        '/api/%s/organisations/<int:org_id>' % api_version,
        '/api/%s/organisations/' % api_version
    )

    api.add_resource(
        ExportOgranisationsResource,
        '/api/%s/export/organisations/' % api_version
    )

    api.add_resource(
        OrganisationPersonsResource,
        '/api/%s/organisations/<int:org_id>/persons/' % api_version,
        '/api/%s/organisations/<int:org_id>/persons/<int:person_id>' % api_version
    )

    api.add_resource(
        UmbrellaOrganisationResource,
        '/api/%s/umbrella_organisations/<int:umb_org_id>' % api_version,
        '/api/%s/umbrella_organisations/<string:umb_org_name>' % api_version,
        '/api/%s/umbrella_organisations/' % api_version
    )

    api.add_resource(
        UmbrellaOrganisationPersonsResource,
        '/api/%s/umbrella_organisations/<int:umb_org_id>/persons/' % api_version,
        '/api/%s/umbrella_organisations/<int:umb_org_id>/persons/<int:person_id>' % api_version
    )

    api.add_resource(
        UmbrellaOrgMemberOrgAssociationsResource,
        '/api/%s/umbrella_organisations/<int:umbrella_organisation_id>/organisations/' % api_version,
        '/api/%s/umbrella_organisations/<int:umbrella_organisation_id>/organisations/<int:association_id>' % api_version
    )

    api.add_resource(
        BrregActivityCodeResource,
        '/api/%s/brreg_activity_codes/' % api_version
    )

    api.add_resource(
        FlodActivityTypeResource,
        '/api/%s/flod_activity_types/' % api_version
    )

    api.add_resource(
        DistrictResource,
        '/api/%s/districts/' % api_version
    )

    api.add_resource(
        OrganisationInternalNotesResource,
        '/api/%s/organisations/<int:organisation_id>/notes/' % api_version,
        '/api/%s/organisations/<int:organisation_id>/notes/<int:note_id>' % api_version
    )

    @app.route('/api/%s/brreg/enhet' % api_version)
    def lookup_basic_brreg_data():
        """
        Lookup unit information in Brreg.

        :param orgnr: Organisation number
        :statuscode 401: Unauthorized
        """
        if not verify_auth_token(request.cookies.get('auth_token')):
            abort(401)
        if not brreg_client:
            abort(404)
        org_number = request.args['orgnr']
        try:
            response = brreg_client.get_brreg_enhet_basis_data_full(org_number)
        except OrgNrNotFoundException, e:
            return Response(
                json.dumps({"__error__": [e.message]}),
                mimetype='application/json',
                status=404
            )

        try:
            flod_org = current_app.db_session.query(Organisation).filter(
                Organisation.org_number == org_number
            ).one()
            response['id'] = flod_org.id
            is_registered = not flod_org.is_deleted
        except NoResultFound:
            is_registered = False

        response['is_registered'] = is_registered

        marshalled = marshal(response, brreg_org_fields)
        return Response(
            json.dumps(marshalled),
            mimetype='application/json'
        )

    @app.route('/api/%s/brreg/enhet/roller' % api_version)
    def lookup_brreg_roles():
        """
        Lookup roles in Brreg.

        :param orgnr: Organisation number
        :statuscode 401: Unauthorized
        """
        if not verify_auth_token(request.cookies.get('auth_token')):
            abort(401)
        if not brreg_client:
            abort(404)
        org_number = request.args['orgnr']
        response = brreg_client.get_brreg_enhet_role_data(org_number)
        return Response(json.dumps(response), mimetype='application/json')

    @app.route('/api/%s/brreg/enhet/kontakt' % api_version)
    def lookup_brreg_contact():
        """
        Lookup contact information in Brreg.

        :param orgnr: Organisation number
        :statuscode 401: Unauthorized
        """
        if not verify_auth_token(request.cookies.get('auth_token')):
            abort(401)
        if not brreg_client:
            abort(404)
        org_number = request.args['orgnr']
        response = brreg_client.get_brreg_enhet_contact_data(org_number)
        return Response(json.dumps(response), mimetype='application/json')

    @app.route('/api/%s/brreg/search' % api_version)
    def lookup_org_name():
        """
        Lookup organisation in Brreg by name.

        :param name: Organisation name
        :statuscode 401: Unauthorized
        """
        if not verify_auth_token(request.cookies.get('auth_token')):
            abort(401)
        if not brreg_client:
            abort(404)
        name = request.args['name']
        response = brreg_client.get_brreg_enhet_name_search(name)
        search_result = response.get('result', [])
        for org in search_result:
            org_number = org.get('Orgnr', None)
            try:
                flod_org = current_app.db_session.query(Organisation).filter(
                    Organisation.org_number == org_number
                ).one()
                org['id'] = flod_org.id

                org['is_registered'] = not flod_org.is_deleted
            except NoResultFound:
                org['is_registered'] = False

        marshalled = marshal(search_result, brreg_name_search_fields)
        return Response(json.dumps(marshalled), mimetype='application/json')

    return api