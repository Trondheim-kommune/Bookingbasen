#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app
from flask.ext import restful
from flask.ext.restful import fields, marshal
from collections import OrderedDict
from flod_common.outputs.output_csv import output_csv

from domain.models import Address, Organisation, Person, \
    BrregActivityCode, FlodActivityType, UmbrellaOrganisation, \
    PersonOrgAssociationRole, OrganisationPersonAssociation, \
    UmbrellaOrgMemberOrgAssociation, OrganisationInternalNote, District
from validation.role_validators import (UserHasOrganisationAdminRoleValidator)
from api import person_fields_admin, role_fields, address_fields, flod_activity_type_fields


person_roles_for_report = {
    'person': fields.Nested(person_fields_admin),
    'roles': fields.List(fields.Nested(role_fields))
}

brreg_activity_code_fields_for_report = {
    'description': fields.String(default=None)
}


organisation_fields_admin_for_report = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None),
    'org_number': fields.String(default=None),
    'org_form': fields.String(default=None),
    'account_number': fields.String(default=None),

    'email_address': fields.String(default=None),
    'local_email_address': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'telefax_number': fields.String(default=None),
    'url': fields.String(default=None),
    'uri': fields.String(default=None),

    'tilholdssted_address': fields.Nested(address_fields, allow_null=True),
    'business_address': fields.Nested(address_fields, allow_null=True),
    'postal_address': fields.Nested(address_fields, allow_null=True),
    'is_public': fields.Boolean,

    # activity codes
    'brreg_activity_codes': fields.List(fields.Nested(brreg_activity_code_fields_for_report, allow_null=True), default=[]),

    'people': fields.List(fields.Nested(person_roles_for_report, allow_null=True), default=[]),

    # Trondheim kommune specific fields
    'flod_activity_types': fields.List(fields.Nested(flod_activity_type_fields, allow_null=True), default=[]),
    'num_members_b20': fields.Integer(default=None),
    'num_members': fields.Integer(default=None),
    'description': fields.String(default=None),
    'area': fields.Integer(default=None),
    'recruitment_area': fields.Integer(default=None),
    'registered_tkn': fields.Boolean,
    'relevant_tkn': fields.Boolean,
    'is_registered': fields.Boolean,
    'is_deleted': fields.Boolean
}

def get_fieldname_mapping():
    fieldname_mapping = OrderedDict()
    fieldname_mapping['name'] = 'Aktørens navn'
    fieldname_mapping['org_number'] = 'Organisasjonsnummer'
    fieldname_mapping['org_form'] = 'Organisasjonsform'

    fieldname_mapping['brreg_activity_codes_description'] = 'Kategori(er)'
    fieldname_mapping['flod_activity_types_name'] = 'Organisasjonens aktivitet(er)'

    fieldname_mapping['phone_number'] = 'Telefon'
    fieldname_mapping['telefax_number'] = 'Telefax'
    fieldname_mapping['email_address'] = 'Epost'
    fieldname_mapping['local_email_address'] = 'Epost 2'

    fieldname_mapping['recruitment_area'] = 'Rekrutteringsområde'

    fieldname_mapping['tilholdssted_address_address_line'] = 'Primært tilholdssted'
    fieldname_mapping['area'] = 'Bydel'
    fieldname_mapping['tilholdssted_address_postal_code'] = 'Postnummer'
    fieldname_mapping['tilholdssted_address_postal_city'] = 'Poststed'

    fieldname_mapping['business_address_address_line'] = 'Forretningsadresse'
    fieldname_mapping['business_address_postal_code'] = 'Postnummer'
    fieldname_mapping['business_address_postal_city'] = 'Poststed'

    fieldname_mapping['postal_address_address_line'] = 'Postadresse'
    fieldname_mapping['postal_address_postal_code'] = 'Postnummer'
    fieldname_mapping['postal_address_postal_city'] = 'Poststed'

    fieldname_mapping['account_number'] = 'Kontonummer'
    fieldname_mapping['num_members'] = 'Antall medlemmer'
    fieldname_mapping['num_members_b20'] = 'Antall medlemmer under 20 år'

    fieldname_mapping['relevant_tkn'] = 'Relevant for Trondheim kulturnettverk'
    fieldname_mapping['registered_tkn'] = 'Medlem i Trondheim kulturnettverk'
    fieldname_mapping['is_public'] = 'Samtykker til visning av informasjon på nett'

    fieldname_mapping['description'] = 'Beskrivelse'
    fieldname_mapping['url'] = 'url'

    fieldname_mapping['people_person_first_name'] = 'Fornavn'
    fieldname_mapping['people_person_last_name'] = 'Etternavn'
    fieldname_mapping['people_person_email_address'] = 'E-post-adresse'
    fieldname_mapping['people_person_phone_number'] = 'Telefon'
    fieldname_mapping['people_roles_role'] = 'Rolle'

    return fieldname_mapping

def get_fields_to_ignore():
    fields_to_ignore = [
        'id',
        'postal_address',
        'business_address',
        'tilholdssted_address',
        'brreg_activity_codes',
        'flod_activity_types',
        'flod_activity_types_id',
        'is_deleted',
        'uri',
        'is_registered',
        'people_roles',
        'people_person_roles',
        'people_person_uri',
        'people_person_postal_city',
        'people_person_postal_code',
        'people_person_address_line',
        'people_person_status',
        'people_person_national_identity_number',
        'people_roles_id',
        'people_person_id'
    ]
    return fields_to_ignore

class ExportOgranisationsResource(restful.Resource):

    @UserHasOrganisationAdminRoleValidator()
    def get(self):
        organisations = current_app.db_session.query(Organisation)
        organisations = organisations.filter(Organisation.is_deleted == False)

        districts = current_app.db_session.query(District)
        distr = districts.all()

        d = dict([(dd.id, dd.name) for dd in distr])

        orgs = organisations.order_by(Organisation.name).all()
        marshalled_org = marshal(orgs, organisation_fields_admin_for_report)

        for org in marshalled_org:
            if org["recruitment_area"] is not None:
                org["recruitment_area"] = d.get(int(org["recruitment_area"]), "")

            if org["area"] is not None:
                org["area"] = d.get(int(org["area"]), "")

        return output_csv(marshalled_org, 200, fieldname_mapping=get_fieldname_mapping(), fields_to_ignore=get_fields_to_ignore())
