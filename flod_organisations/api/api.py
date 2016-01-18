# -*- coding: utf-8 -*-
import json

import os
import re
from flask import current_app, request, Response
from flask.ext import restful
from flask.ext.restful import abort, fields, marshal_with, marshal
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound
import requests
from sqlalchemy import and_
from flod_common.validation.base_validator import BaseValidator
from validation.organisation_validator import OrganisationValidator
from domain.models import Address, Organisation, Person, \
    BrregActivityCode, FlodActivityType, UmbrellaOrganisation, \
    PersonOrgAssociationRole, OrganisationPersonAssociation, \
    UmbrellaOrgMemberOrgAssociation, OrganisationInternalNote, District
from flod_common.session.utils import (unsign_auth_token,
                                       verify_superuser_auth_token)
import repo
from util.brregclient import BrRegClient, OrgNrNotFoundException
from validation.authentication_validators import UserIsCookieAuthenticatedValidator
from validation.role_validators import (UserHasAdminRoleValidator,
                                        UserHasOrganisationAdminRoleValidator)
from validation.base_validators import OrValidator
from repo import is_administrator, has_role
from flod_common.session.utils import make_superuser_auth_cookie

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


def get_int_value(str_val):
    try:
        return int("".join(re.findall('\d', str(str_val))))
    except ValueError:
        return -1


class ISO8601DateTime(fields.Raw):
    def __init__(self, default=None, attribute=None):
        super(ISO8601DateTime, self).__init__(default, attribute)

    def format(self, value):
        if not value:
            return self.default
        return value.isoformat()


flod_activity_type_fields = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None)
}

brreg_activity_code_fields = {
    'code': fields.String(default=None),
    'description': fields.String(default=None),
    'flod_activity_types': fields.List(fields.Nested(flod_activity_type_fields))
}

district_fields = {
    'id': fields.Integer,
    'name': fields.String
}

address_fields = {
    'address_line': fields.String(default=None),
    'postal_code': fields.String(default=None),
    'postal_city': fields.String(default=None),
}

person_fields_short = {
    'id': fields.Integer(default=None),
    'uri': fields.String(default=None),
    'first_name': fields.String(default=None),
    'last_name': fields.String(default=None),
}

role_fields = {
    'id': fields.Integer,
    'role': fields.String(default=None)
}

person_fields = {
    'id': fields.Integer(default=None),
    'uri': fields.String(default=None),
    'first_name': fields.String(default=None),
    'last_name': fields.String(default=None),
    'status': fields.String(default=None),
    'roles': fields.List(fields.Nested(role_fields)),
    'email_address': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'address_line': fields.String(default=None),
    'postal_code': fields.String(default=None),
    'postal_city': fields.String(default=None),
}

person_fields_admin = {
    'id': fields.Integer(default=None),
    'uri': fields.String(default=None),
    'first_name': fields.String(default=None),
    'last_name': fields.String(default=None),
    'status': fields.String(default=None),
    'roles': fields.List(fields.Nested(role_fields)),
    'email_address': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'address_line': fields.String(default=None),
    'postal_code': fields.String(default=None),
    'postal_city': fields.String(default=None),
    'national_identity_number': fields.String(default=None)
}

organisation_fields_short = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None),
    'org_number': fields.String(default=None),
    'uri': fields.String(default=None)
}

organisation_fields_only_name = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None),
    'org_number': fields.String(default=None),
    'uri': fields.String(default=None),
    'is_deleted': fields.Boolean,
    'is_public': fields.Boolean,
    'only_name': fields.String(default=True)
}

organisation_fields = {
    'id': fields.Integer(default=None),
    'name': fields.String(default=None),
    'org_number': fields.String(default=None),
    'org_form': fields.String(default=None),

    'phone_number': fields.String(default=None),
    'telefax_number': fields.String(default=None),
    'url': fields.String(default=None),
    'uri': fields.String(default=None),

    'tilholdssted_address': fields.Nested(address_fields, allow_null=True),
    'business_address': fields.Nested(address_fields, allow_null=True),
    'postal_address': fields.Nested(address_fields, allow_null=True),

    # activity codes
    'brreg_activity_code': fields.List(fields.String),

    # Trondheim kommune specific fields
    'flod_activity_type': fields.List(fields.Integer, default=[]),
    'num_members_b20': fields.Integer(default=None),
    'num_members': fields.Integer(default=None),
    'description': fields.String(default=None),
    'area': fields.Integer(default=None),
    'recruitment_area': fields.Integer(default=None),
    'is_registered': fields.Boolean,
    'is_deleted': fields.Boolean,
}

# organisation w. account number and email
# for admin eyes only (and the person/org in question)
organisation_fields_admin = {
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
    'brreg_activity_code': fields.List(fields.String),

    # Trondheim kommune specific fields
    'flod_activity_type': fields.List(fields.Integer, default=[]),
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

umbrella_organisation_fields = {
    'id': fields.Integer(default=None),
    'uri': fields.String,
    'name': fields.String(default=None),
    'organisations': fields.List(fields.Nested(organisation_fields_short)),
    'persons': fields.List(fields.Nested(person_fields_short)),
    'is_deleted': fields.Boolean
}

umbrella_org_member_org_association_fields = {
    'id': fields.Integer(default=None),
    'organisation_id': fields.Integer(default=None),
    'umbrella_organisation_id': fields.String(default=None),
    'organisation': fields.Nested(organisation_fields_short)
}

organisation_internal_note_fields = {
    'id': fields.Integer,
    'auth_id': fields.String,
    'organisation_id': fields.Integer,
    'text': fields.String,
    'create_time': ISO8601DateTime,
}


def find_person(nin):
    result = current_app.db_session.query(Person)
    result = result.filter(Person.national_identity_number == nin)
    return result.first()


def get_person_from_username(request):
    auth_token = request.cookies.get('auth_token', None)
    if not auth_token:
        return None, False

    if verify_superuser_auth_token(auth_token):
        return None, True

    username = unsign_auth_token(auth_token)

    url = '%s/api/v1/users/%s' % (USERS_URL, username)
    response = requests.get(url, cookies=request.cookies)

    if response.status_code == 200:
        data = response.json()
        nin = data["profile"]["national_id_number"]

        current_app.logger.debug("Current user nin is %s" % nin)
        return find_person(nin), is_administrator(data)
    else:
        return None, False


class PersonsResource(restful.Resource):
    @UserIsCookieAuthenticatedValidator()
    @marshal_with(person_fields_admin)
    def get(self):
        data = request.get_json(silent=True)
        person_ids = data.get('person_ids') if data else None

        if not is_user_tk_admin(request):
            # only admins are allowed to get list of users.
            # If changed later, remember to change field-set used to marshal with, as only admins are allowed to see national_identity_number
            abort(401)
        result = current_app.db_session.query(Person).order_by(
            Person.last_name)

        if person_ids:
            result = result.filter(Person.id.in_(person_ids))

        if "national_identity_number" in request.args:
            nin = request.args["national_identity_number"]
            result = result.filter(Person.national_identity_number == nin)
            try:
                return result.one()
            except NoResultFound:
                abort(404)

        return result.all()


class PersonOrganisationsResource(restful.Resource):
    @UserIsCookieAuthenticatedValidator()
    @marshal_with(organisation_fields_short)
    def get(self, person_id=None):

        if person_id is None:
            return []

        person = current_app.db_session.query(Person).filter(
            Person.id == person_id
        ).first()

        if person is None:
            abort(404, __error__=['Fant ingen person med id=%s ' % person_id])

        user_person, is_admin = get_person_from_username(request)

        # Non-admins should only be able to retrieve their own person
        if not is_admin and user_person.id != person.id:
            abort(401)

        return [person_org_assoc.organisation
                for person_org_assoc in person.organisations]


def is_user_tk_admin(request):
    auth_token = request.cookies.get('auth_token', None)
    username = unsign_auth_token(auth_token)
    # The "super user" is allowed to create orgs on behalf of others
    super_username = os.environ['AUTH_ADMIN_USER_ID']
    if username == super_username:
        return True

    url = '%s/api/v1/users/%s' % (USERS_URL, username)
    response = requests.get(url, cookies=request.cookies)
    if response.status_code == 200:
        data = response.json()
        if is_administrator(data):
            return True
    return False


def check_user(request, registered_people, org_name, type):
    auth_token = request.cookies.get('auth_token', None)
    username = unsign_auth_token(auth_token)

    # The "super user" is allowed to create orgs on behalf of others
    super_username = os.environ['AUTH_ADMIN_USER_ID']
    if username == super_username:
        return True, True

    url = '%s/api/v1/users/%s' % (USERS_URL, username)
    response = requests.get(url, cookies=request.cookies)
    current_app.logger.debug("Registered persons for org '%s': %s" % (org_name, ", ".join(registered_people)))

    if response.status_code == 200:
        data = response.json()
        if has_role(data, u'flod_aktørregister_admin'):
            return True, True
        else:
            nin = data["profile"]["national_id_number"]
            current_app.logger.debug("Current user nin is %s" % nin)
            if nin in registered_people:
                return True, False
            else:
                abort(
                    403,
                    __error__=['Brukeren er ikke en av personene '
                               'assosiert med %s i Brønnøysundregistrene eller '
                               'Aktørbasen og kan derfor ikke %s denne '
                               'organisasjonen.'.decode("utf-8") % (org_name, type)]
                )
    else:
        abort(400, __error__=["Noe gikk galt ved sjekk av rettigheter."])


class OrganisationPersonsResource(restful.Resource):
    def find_org(self, org_id):
        if not org_id:
            abort(400, __error__=['org_id mangler'])

        result = current_app.db_session.query(Organisation).filter(
            Organisation.id == org_id
        )
        try:
            org = result.one()
            return org
        except Exception:
            abort(
                404,
                __error__=['Fant ingen organisasjon med id=%s ' % org_id]
            )

    def find_person(self, national_identity_number=None):
        if not national_identity_number:
            abort(400, __error__=['Personnummer mangler'])
        result = current_app.db_session.query(Person). \
            filter(Person.national_identity_number == national_identity_number)
        try:
            return result.one()
        except NoResultFound:
            return None

    def is_owner(self, person, persons):
        if person is None:
            return False
        return person.id in (p.id for p in persons)

    def get(self, org_id, person_id=None):
        """
        Get members (persons) of an organisation.

        :param org_id: ID of organisation
        :statuscode 200: No error
        """
        org = self.find_org(org_id)
        person, is_admin = get_person_from_username(request)
        is_adhoc_org = org.org_number is None
        is_anonymous = person is None and not is_admin
        empty_response = marshal([], {}), 200

        assocs = current_app.db_session.query(OrganisationPersonAssociation) \
            .filter(OrganisationPersonAssociation.organisation_id == org.id) \
            .join(Organisation) \
            .join(Person) \
            .order_by(Person.last_name)

        # Anonymous users should only see persons in public organisations
        # with orgnr
        visible_fields = person_fields_short
        if is_anonymous:
            assocs = assocs.filter(Organisation.org_number != None,
                                   Organisation.is_public == True)

            # Hide some fields from anonymous users
            visible_fields = person_fields_short

            # Anonymous can't list all persons
            if person_id is None:
                return empty_response

        persons = []
        roles = {}

        for assoc in assocs.all():
            assoc.person.from_brreg = assoc.from_brreg

            str_role = assoc.roles
            roles[str(assoc.person.id)] = str_role

            persons.append(assoc.person)

        # Only admins and owners should see persons in adhoc organisations
        # or non-public orgs
        if (is_adhoc_org or not org.is_public) and not is_admin and not self.is_owner(person, persons):
            return empty_response

        if person_id is not None:
            persons = [p for p in persons if p.id == person_id]

        if is_admin or self.is_owner(person, persons):
            visible_fields = person_fields

        visible_fields['from_brreg'] = fields.Boolean

        persons_with_roles = marshal(persons, visible_fields)
        for pers in persons_with_roles:
            pers["roles"] = marshal(roles[str(pers["id"])], role_fields)

        return persons_with_roles, 200

    def find_person_association_in_org(self, org, person_id):
        for org_person_assoc in org.people:
            if org_person_assoc.person.id == person_id:
                return org_person_assoc
        return None

    @marshal_with(person_fields)
    def post(self, org_id, person_id=None):
        """
        Create a new member (person) of an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/organisations/123/persons/ HTTP/1.1
           Content-Type: application/json

           {
               "national_identity_number": "05058512345"
           }

        :param org_id: ID of organisation
        :statuscode 201: No error
        :statuscode 400: Invalid national identity number
        :statuscode 409: Person is already a member
        :statuscode 403: User does not have permission to edit organisation
        :statuscode 401: Unauthorized
        """
        org = self.find_org(org_id)

        registered_people = [p.national_identity_number for p in org.persons]
        can_edit, is_admin = check_user(request, registered_people, org.name, 'opprette')

        if not can_edit:
            abort(403, __error__=[(u'Brukeren har ikke tillatelse til å '
                                   u'redigere {}'.format(org))])

        data = request.get_json()

        nin = data.get('nin')
        person = self.find_person(nin)
        if person is None:
            if len(nin) != 11 or not nin.isdigit():
                abort(400, __error__=[u'Fødselsnummer må bestå av 11 siffer'])
            person = Person(nin)
            person.first_name = data.get('first_name')
            person.last_name = data.get('last_name')

            if is_admin:
                validator = BaseValidator(data)
                validator.validate_is_email("email_address", label="E-post", requires_value=False)
                validator.validate_is_norwegian_phone_number("phone_number", label="Telefonnummer",
                                                             requires_value=False)

                if validator.has_errors():
                    abort(400, __error__=validator.errors)

                if data.get('email_address'):
                    person.email_address = data.get('email_address')

                if data.get('phone_number'):
                    person.phone_number = data.get('phone_number')

            else:
                if data.get('email_address') or data.get('phone_number'):
                    abort(400, __error__=[u'Kun admin har tillatelse til å sette epost og telefon'])

            current_app.db_session.add(person)

        org_person_assosication = current_app.db_session.query(
            OrganisationPersonAssociation).filter(and_(
            OrganisationPersonAssociation.person_id == person.id,
            OrganisationPersonAssociation.organisation_id == org_id)).first()
        if org_person_assosication is not None:
            abort(409, __error__=[(u'En person med dette fødselsnummeret er '
                                   u'allerede lagt til på organisasjonen')])

        try:
            org_person_association = OrganisationPersonAssociation(person)
            current_app.db_session.add(org_person_association)
            org.add_person_association(org_person_association)
            current_app.db_session.commit()
        except IntegrityError:
            abort(400, __error__=[(u'En person med denne adressen er '
                                   u'allerede lagt til på organisasjonen')])

        return person, 201

    def delete(self, org_id, person_id=None):
        """
        Delete a member (person) of an organisation.

        **Example request**:

        .. sourcecode:: http

           DELETE /api/v1/organisations/123/persons/321 HTTP/1.1

        :statuscode 204: No error
        :statuscode 401: Unauthorized
        :statuscode 403: Attempt to delete person imported from Brreg
        :statuscode 404: Missing person ID
        :statuscode 404: Person is not associated with umbrella organisation
        """
        org = self.find_org(org_id)

        if not person_id:
            data = request.get_json()
            if data:
                person_id = data.get('id')

        if not person_id:
            abort(404, __error__=["Mangler person-id."])

        registered_people = [p.national_identity_number for p in org.persons]
        can_edit, is_admin = check_user(request, registered_people, org.name, 'slette')
        if can_edit:
            person_organisation_association = self.find_person_association_in_org(org, person_id)
            if not person_organisation_association:
                abort(
                    404,
                    __error__=["Personen med id=%s "
                               "er ikke assosiert med organisasjonen." % person_id]
                )
            if person_organisation_association.from_brreg:
                abort(
                    403,
                    __error__=["Kan ikke slette person importert fra brreg."]
                )
            current_app.db_session.delete(person_organisation_association)
            current_app.db_session.commit()
            return "", 204


def parse_person_data(person, data):
    person.first_name = data.get("first_name", None)
    person.last_name = data.get("last_name", None)
    person.email_address = data.get("email_address", None)
    person.phone_number = data.get("phone_number", None)
    person.address_line = data.get("address_line", None)
    person.postal_city = data.get("postal_city", None)
    person.postal_code = data.get("postal_code", None)
    return person


class PersonResource(restful.Resource):
    @staticmethod
    def get_person(person_id):
        try:
            return current_app.db_session.query(Person).filter(
                Person.id == person_id
            ).one()
        except NoResultFound:
            return None

    @UserIsCookieAuthenticatedValidator()
    def get(self, person_id):
        """
        Get person given a person ID.

        Only own person is returned for non-admins.

        :param person_id: ID for person, if omitted, all persons are returned.
        :statuscode 200: No error
        :statuscode 401: Unauthorized
        :statuscode 404: Person does not exist
        """
        user_person, is_admin = get_person_from_username(request)
        person = self.get_person(person_id)
        if person is None:
            return self.__make_error_dict("Brukeren eksisterer ikke"), 404

        # Non-admins should only be able to retrieve their own person
        if not is_admin and user_person.id != person.id:
            abort(401)

        # Include nin if person is requested by an admin user
        if is_admin:
            return marshal(person, person_fields_admin), 200

        return marshal(person, person_fields), 200

    @UserIsCookieAuthenticatedValidator()
    def post(self):
        """
        Create a new person.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/persons HTTP/1.1
           Content-Type: application/json

           {
               "national_identity_number": "05058512345"
           }

        :statuscode 201: Person created
        :statuscode 400: Missing national identity number in request
        :statuscode 400: Person with nin already exists
        :statuscode 401: Unauthorized
        """
        data = request.get_json()
        try:
            national_identity_number = data.pop("national_identity_number")
        except KeyError:
            return self.__make_error_dict({
                "national_identity_number": "Må være satt!"
            }), 400

        person = Person(national_identity_number)
        person = parse_person_data(person, data)
        person.status = "unregistered"

        validator = BaseValidator(data)
        validator.validate_is_name("first_name", "Fornavn", requires_value=False)
        validator.validate_is_name("last_name", "Etternavn", requires_value=False)
        validator.validate_is_email("email_address", label="E-post", requires_value=False)
        validator.validate_is_norwegian_phone_number("phone_number", label="Telefonnummer", requires_value=False)

        if validator.has_errors():
            abort(400, __error__=validator.errors)

        current_app.db_session.add(person)
        try:
            current_app.db_session.commit()
        except IntegrityError:
            return self.__make_error_dict("Brukeren eksisterer fra før!"), 400
        current_app.db_session.refresh(person)
        marshaled = marshal(person, person_fields)
        return Response(json.dumps(marshaled), 201, mimetype='application/json')

    def is_person(self, user, person_id):
        if user is None:
            return False
        return user.get('person_id') == person_id

    @UserIsCookieAuthenticatedValidator()
    def put(self, person_id):
        """
        Update a existing person.

        **Example request**:

        .. sourcecode:: http

           PUT /api/v1/persons/123 HTTP/1.1
           Content-Type: application/json

           {
               "email_address": "eggs@spam.tld",
               "phone_number": "12345678"
           }

        :statuscode 200: Person updated
        :statuscode 400: Invalid phone number
        :statuscode 400: Invalid or duplicate email address
        :statuscode 401: Unauthorized
        :statuscode 404: Person not found
        """

        _, is_admin = get_person_from_username(request)
        person = self.get_person(person_id)
        if person is None:
            return self.__make_error_dict("Fant ikke brukeren!"), 404

        user = repo.get_user(request.cookies)

        if not (self.is_person(user, person_id) or is_admin):
            abort(401)

        data = request.get_json()
        validator = BaseValidator(data)

        if is_admin:
            person.email_address = data.get("email_address", None)
            person.phone_number = data.get("phone_number", None)
        else:
            person = parse_person_data(person, data)

            validator.validate_is_name("first_name", "Fornavn")
            validator.validate_is_name("last_name", "Etternavn")

            if person.first_name and person.last_name \
                    and person.email_address and person.phone_number:
                person.status = "registered"

        validator.validate_is_email("email_address", label="E-post")
        validator.validate_is_norwegian_phone_number("phone_number", label="Telefonnummer")

        if validator.has_errors():
            abort(400, __error__=validator.errors)

        try:
            current_app.db_session.add(person)
            current_app.db_session.commit()
            current_app.db_session.refresh(person)
        except IntegrityError:
            return self.__make_error_dict({
                "email_address": "Adressen er i bruk"
            }), 400
        except DataError:
            return self.__make_error_dict({
                "phone_number": "Ugyldig telefonnummer."
            }), 400

        marshaled = marshal(person, person_fields)
        return Response(json.dumps(marshaled), mimetype='application/json')

    @staticmethod
    def __make_error_dict(error_message):
        return {"__error__": [error_message]}


def set_attribute(obj, attr, values, mapping=None):
    value = values.get(attr, None)
    if attr in values:
        if mapping:
            value = mapping(value)
        setattr(obj, attr, value)


def is_phone_number(str):
    if not str:
        return True
    if len(str) != 8:
        return False
    if not str.isnumeric():
        return False
    return True


class OrganisationResource(restful.Resource):
    def parse_contact_info(self, response):
        contact_fields = [
            'phone_number',
            'telefax_number',
            'url',
            'email_address'
        ]
        contactinfo = {}
        for field in contact_fields:
            contactinfo[field] = response[field]
        return contactinfo

    def is_postal_code_valid(self, postal_code):
        if not re.match("^\d{4}$", postal_code):
            return False
        return True

    def parse_address_data(self, address_data):
        if not address_data:
            return None
        address_line = address_data.get('address_line', None)
        postal_code = address_data.get('postal_code', None)
        postal_city = address_data.get('postal_city', None)
        address = Address(address_line, postal_code, postal_city)
        return address

    def find_or_create_person_org_role(self, role_name):
        role = current_app.db_session.query(PersonOrgAssociationRole).filter(
            PersonOrgAssociationRole.role == role_name
        ).first()
        if role:
            return role

        role = PersonOrgAssociationRole(role_name)
        current_app.db_session.add(role)
        return role

    def find_or_create_person_from_brreg_response(self, person):
        national_identity_number = person.pop("national_identity_number", None)
        if not national_identity_number:
            return None

        flod_person = find_person(national_identity_number)

        if not flod_person:
            flod_person = Person(national_identity_number, **person)
            current_app.db_session.add(flod_person)

        return flod_person

    def create_org_person_associations(self, org, people):
        for p in people:
            person = self.find_or_create_person_from_brreg_response(p)
            if not person:
                continue
            person_org_roles = []
            for role_name in p.get('org_roles'):
                person_org_roles.append(self.find_or_create_person_org_role(role_name))
            org_person_association = OrganisationPersonAssociation(
                person,
                from_brreg=True,
                roles=person_org_roles
            )

            current_app.db_session.add(org_person_association)
            org.add_person_association(org_person_association)

    def create_org_from_name(self, data):
        parameters = {}
        validator = OrganisationValidator(data).validate_post_fields()

        if validator.has_errors():
            abort(400, __error__=validator.errors)

        contact_fields = [
            'name',
            'phone_number',
            'telefax_number',
            'url',
            'email_address',
            'local_email_address'
        ]
        for field in contact_fields:
            parameters[field] = data.get(field, None)
            if parameters[field] and field in ['phone_number', 'telefax_number']:
                parameters[field] = ''.join(e for e in parameters[field] if e.isalnum())

        if data.get('postal_address', None):
            parameters['postal_address'] = self.parse_address_data(
                data['postal_address']
            )
        if data.get('business_address', None):
            parameters['business_address'] = self.parse_address_data(
                data['business_address']
            )
        if data.get('tilholdssted_address', None):
            parameters['tilholdssted_address'] = self.parse_address_data(
                data['tilholdssted_address']
            )

        flod_fields = ['area', 'recruitment_area']
        if is_user_tk_admin(request):
            flod_fields += ['num_members', 'num_members_b20']

        for field in flod_fields:
            if field in data:
                value = get_int_value(data.get(field))
                if value != -1:
                    parameters[field] = value
        if data.get('description', None):
            parameters['description'] = data['description']

        parameters['is_public'] = data.get('is_public', False)

        # The user which creates the adhoc organisation owns it
        role = self.find_or_create_person_org_role("owner")
        person, is_admin = get_person_from_username(request)

        if is_admin:
            parameters['relevant_tkn'] = data.get('relevant_tkn', False)

        org = Organisation(**parameters)

        # Add person to org if the org is not created by admin
        if person and not is_admin:
            org_person_association = OrganisationPersonAssociation(
                person,
                from_brreg=False,
                roles=[role]
            )

            current_app.db_session.add(org_person_association)
            org.add_person_association(org_person_association)

        return org

    @UserIsCookieAuthenticatedValidator()
    def create_org_from_org_data(self, data):
        if not brreg_client:
            abort(400, __error__=['Kunne ikke koble til brreg'])
        org_number = data['org_number']
        if not org_number:
            abort(400, __error__=['Organisasjonsnummer mangler.'])
        org_number = "".join(re.findall('\d', str(org_number)))
        if len(org_number) != 9:
            abort(400, __error__=['Ugyldig organisationsnummer.'])

        existing_org = current_app.db_session.query(Organisation).filter(
            Organisation.org_number == org_number
        ).all()
        if existing_org:
            abort(
                403,
                __error__=['Organisasjonen %s finnes fra før.' % org_number]
            )

        try:
            brreg_response = brreg_client.get_brreg_enhet_basis_data_full(
                org_number
            )
        except OrgNrNotFoundException, e:
            return Response(
                json.dumps({"__error__": [e.message]}),
                mimetype='application/json',
                status=404
            )

        if not brreg_response:
            abort(
                400,
                __error__=['Fikk ikke gyldig respons fra brreg.']
            )
        status = brreg_response.get('response_status')
        if int(status.get('code')) > 0:
            abort(400, __error__=[status.get('message')])


        # Building a set will avoid getting duplicates.
        # It seems that the same person, with the same national id number can occur several times in the list
        # returned by broennoeysund, with slightly variying metadata.
        registered_people = set(
            [x.get('national_identity_number') for x
             in brreg_response.get('persons')]
        )

        can_edit, is_admin = check_user(request, registered_people, brreg_response['name'], 'opprette')

        parameters = {'org_number': org_number}
        brreg_fields = [
            'name',
            'org_form',
            'brreg_activity_code',
            'account_number'
        ]
        for field in brreg_fields:
            parameters[field] = brreg_response.get(field, None)

        contactinfo = self.parse_contact_info(brreg_response)
        parameters.update(contactinfo)

        for address_data in ['postal_address', 'business_address']:
            if brreg_response.get(address_data):
                address = self.parse_address_data(brreg_response[address_data])
                if address:
                    current_app.db_session.add(address)
                    parameters[address_data] = address

        fields = ['area', 'description', 'recruitment_area']
        if is_admin:
            fields += ['num_members', 'num_members_b20']

        validator = OrganisationValidator(data).validate_extra_fields()

        if validator.has_errors():
            abort(400, __error__=validator.errors)

        for field in fields:
            parameters[field] = data.get(field) or None

        parameters['registered_tkn'] = data.get('registered_tkn', False)

        if is_admin:
            parameters['relevant_tkn'] = data.get('relevant_tkn', False)
        parameters['is_public'] = data.get('is_public', False)

        org = Organisation(**parameters)

        for code in brreg_response.get('brreg_activity_code', []):
            org.add_brreg_activity_code(code)

        org.add_flod_activity_type(data.get('flod_activity_type', []))

        self.create_org_person_associations(
            org,
            brreg_response.get('persons', [])
        )

        return org

    def extract_org_data(self, data):
        if not data:
            abort(400, __error__=['Manglende data.'])

        if data.get("org_number", None):
            return self.create_org_from_org_data(data)
        if data.get("name", None):
            return self.create_org_from_name(data)
        abort(400, __error__=['Organisasjonsnummer eller navn må fylles ut'])

    def marshal_fields(self, is_admin, include_persons, organisation=None, person=None):
        if is_admin:
            if include_persons:
                persons_field = {'persons': fields.Nested(person_fields_admin)}
                return dict(organisation_fields_admin.items() +
                            persons_field.items())
            return organisation_fields_admin
        org_members = [p.person_id for p in organisation.people]

        if (organisation.is_public and organisation.org_number) or (person is not None and person.id in org_members):
            org_fields = organisation_fields
            if include_persons:
                persons_field = {'persons': fields.Nested(person_fields)}
                org_fields = dict(org_fields.items() + persons_field.items())
        else:
            org_fields = organisation_fields_only_name

        return org_fields

    def marshal_orgs(self, is_admin, include_persons, person, orgs):
        result = []
        for org in orgs:
            json_fields = self.marshal_fields(is_admin, include_persons, organisation=org, person=person)
            result.append(marshal(org, json_fields))
        return result

    def get(self, org_id=None):
        """
        Get organisation(s).

        :param org_id: ID of organisation
        :param name: Filter organisation by name
        :param show_deleted: If True, include deleted organisations in response
        :param include_persons: If True, included persons (members) in response
        :param org_number: Filter organisation by org number
        :param brreg_activity_code: Filter organisation by Brreg activity code
        :param flod_activity_type: Filter organisation by Flod activity type
        :statuscode 200: No error
        :statuscode 400: Unauthorized or organisation not found
        """
        if repo.is_super_admin(cookies=request.cookies):
            person = None
            is_admin = True
        else:
            person, is_admin = get_person_from_username(request)

        # Do not show deleted organisations by default
        show_deleted = request.args.get('show_deleted') == 'True'

        # Do not include persons by default
        include_persons = request.args.get('include_persons') == 'True'

        orgs = current_app.db_session.query(Organisation)

        # ID-porten and anonymous users can only view not deleted orgs
        if not is_admin:
            orgs = orgs.filter(and_(Organisation.is_deleted == False))

        # Hide deleted orgs if not requested
        if not show_deleted:
            orgs = orgs.filter(Organisation.is_deleted == False)

        if org_id:
            org = orgs.filter(Organisation.id == org_id).first()

            if org is None:
                abort(400, __error__=[
                    'Ingen tilgang eller organisasjon ikke funnet'])

            json_fields = self.marshal_fields(is_admin, include_persons, organisation=org, person=person)
            if is_admin or (person and self.is_member_of_org(person.national_identity_number, org)):
                # Force admin fields
                admin_fields = self.marshal_fields(True, include_persons)

                return marshal(org, admin_fields), 200
            return marshal(org, json_fields), 200

        data = request.get_json(silent=True)
        org_ids = data.get('organisation_ids') if data else None
        if org_ids:
            orgs = orgs.filter(Organisation.id.in_(org_ids))

        if "org_number" in request.args:
            orgs = orgs.filter(
                Organisation.org_number == request.args["org_number"]
            )

        if "name" in request.args:
            orgs = orgs.filter(
                Organisation.name.ilike("%" + request.args["name"] + "%")
            )

        if "area" in request.args:
            orgs = orgs.filter(
                Organisation.area == request.args["area"]
            )

        if "brreg_activity_code" in request.args:
            activity_code = request.args["brreg_activity_code"]
            orgs = orgs.join(
                BrregActivityCode,
                Organisation.brreg_activity_codes
            ).filter(
                BrregActivityCode.code == activity_code
            )

        if "flod_activity_type" in request.args:
            flod_activity_type = request.args["flod_activity_type"]
            orgs = orgs.join(
                FlodActivityType,
                Organisation.flod_activity_types
            ).filter(
                FlodActivityType.id == flod_activity_type
            )

        return self.marshal_orgs(is_admin, include_persons, person, orgs.order_by(Organisation.name).all()), 200

    @UserIsCookieAuthenticatedValidator()
    def put(self, org_id):
        """
        Update an organisation.

        **Example request**:

        .. sourcecode:: http

           PUT /api/v1/organisations/123 HTTP/1.1
           Content-Type: application/json

           {
               "name": "My organisation"
           }

        :param org_id: ID of organisation
        :statuscode 200: No error
        :statuscode 400: Missing organisation ID
        :statuscode 400: Organisation not found in Brreg
        :statuscode 400: Field validation error
        :statuscode 401: Unauthorized
        """

        if not org_id:
            abort(400, __error__=["Organisasjonsid mangler"])
        try:
            org = current_app.db_session.query(Organisation).filter(
                Organisation.id == org_id
            ).one()
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen organisasjon med id=%s." % org_id]
            )

        posted_data = request.get_json()

        registered_people = [p.national_identity_number for p in org.persons]

        can_edit, is_admin = check_user(request, registered_people, org.name, 'endre')

        if posted_data.get('update_brreg', None):

            if not brreg_client:
                abort(400, __error__=['Kunne ikke koble til brreg'])

            try:
                brreg_response = brreg_client.get_brreg_enhet_basis_data_full(
                    org.org_number
                )
            except OrgNrNotFoundException, e:
                return Response(
                    json.dumps({"__error__": [e.message]}),
                    mimetype='application/json',
                    status=404
                )

            org.name = brreg_response.get('name', None)
            org.org_form = brreg_response.get('org_form', None)
            org.email_address = brreg_response.get('email_address', None)
            org.phone_number = brreg_response.get('phone_number', None)
            org.telefax_number = brreg_response.get('telefax_number', None)
            org.url = brreg_response.get('url', None)
            org.account_number = brreg_response.get('account_number', None)

            if brreg_response.get('postal_address'):
                if org.postal_address:
                    current_app.db_session.delete(org.postal_address)
                address = self.parse_address_data(
                    brreg_response['postal_address']
                )
                if address:
                    current_app.db_session.add(address)
                    org.postal_address = address

            if brreg_response.get('business_address'):
                if org.business_address:
                    current_app.db_session.delete(org.business_address)
                address = self.parse_address_data(
                    brreg_response['business_address']
                )
                if address:
                    current_app.db_session.add(address)
                    org.business_address = address

            previously_associated_persons = org.people[:]

            # Reset old people list to add the current ones we get from brreg.
            org.people = []
            self.create_org_person_associations(
                org,
                brreg_response.get('persons', [])
            )

            currently_associated_persons_nins = [person.national_identity_number for person in org.persons]

            for previously_associated_person in previously_associated_persons:
                if previously_associated_person.person.national_identity_number not in currently_associated_persons_nins:
                    previously_associated_person.from_brreg = False
                    previously_associated_person.roles = []
                    org.add_person_association(previously_associated_person)

        # FLOD fields
        if 'flod_activity_type' in posted_data:
            org.flod_activity_types = []
            org.add_flod_activity_type(
                posted_data.get('flod_activity_type', [])
            )

        if is_admin:
            set_attribute(org, 'num_members_b20', posted_data)
            set_attribute(org, 'num_members', posted_data)

        set_attribute(org, 'description', posted_data)
        set_attribute(org, 'area', posted_data, get_int_value)
        set_attribute(org, 'recruitment_area', posted_data, get_int_value)

        set_attribute(org, 'registered_tkn', posted_data)

        if is_admin:
            set_attribute(org, 'relevant_tkn', posted_data)

        set_attribute(org, 'is_public', posted_data)

        set_attribute(org, 'tilholdssted_address', posted_data, self.parse_address_data)

        set_attribute(org, 'local_email_address', posted_data)

        if not org.org_number:
            validator = OrganisationValidator(posted_data).validate_put_fields()

            if validator.has_errors():
                abort(400, __error__=validator.errors)

            set_attribute(org, 'name', posted_data)
            set_attribute(org, 'email_address', posted_data)
            set_attribute(org, 'phone_number', posted_data)
            set_attribute(org, 'telefax_number', posted_data)
            set_attribute(org, 'postal_address', posted_data, self.parse_address_data)
            set_attribute(org, 'business_address', posted_data, self.parse_address_data)
        else:
            validator = OrganisationValidator(posted_data).validate_extra_fields()

            if validator.has_errors():
                abort(400, __error__=validator.errors)

        try:
            current_app.db_session.commit()
            current_app.db_session.refresh(org)

        except Exception:
            abort(400, __error__=["Could not commit changes."])

        response = marshal(org, organisation_fields_admin)
        return Response(json.dumps(response), mimetype='application/json')

    @OrValidator(UserIsCookieAuthenticatedValidator(),
                 UserHasAdminRoleValidator())
    def post(self):
        """
        Create an organisation.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/organisations/123 HTTP/1.1
           Content-Type: application/json

           {
               "name": "My organisation"
           }

        :statuscode 201: No error
        :statuscode 400: Constraint violation
        :statuscode 401: Unauthorized
        """
        data = request.get_json()
        orgdata = self.extract_org_data(data)
        try:
            current_app.db_session.add(orgdata)
            current_app.db_session.commit()
            current_app.db_session.refresh(orgdata)
        except Exception as e:
            abort(400, __error__=["Could not commit data: %s" % e.message])
        response = marshal(orgdata, organisation_fields_admin)
        return Response(json.dumps(response), 201, mimetype='application/json')

    def is_member_of_org(self, nin, org):
        registered_people = [p.national_identity_number for p in org.persons]
        current_app.logger.debug("Registered persons for '%s': %s" % (org.name, ", ".join(registered_people)))
        return nin in registered_people

    @OrValidator(UserHasOrganisationAdminRoleValidator(),
                 UserHasAdminRoleValidator())
    def delete(self, org_id):
        """
        Delete an organisation.

        **Example request**:

        .. sourcecode:: http

           DELETE /api/v1/organisations/123 HTTP/1.1

        :statuscode 204: No error
        :statuscode 400: Missing organisation ID
        :statuscode 404: Oranisation does not exist
        :statuscode 401: Unauthorized
        """

        # delete functionality is disabled because it does not check if the organisation is in use in tilskuddsbasen
        abort(501)

        if org_id is None:
            abort(400)
        organisation = current_app.db_session.query(
            Organisation
        ).get(org_id)
        if organisation is None:
            abort(404)
        organisation.is_deleted = True

        auth_token_cookie = make_superuser_auth_cookie()
        cookies = dict(request.cookies.items() + auth_token_cookie.items())
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.delete(organisation_booking_uri + "/" + str(organisation.id), cookies=cookies,
                                   headers=headers)
        if response.status_code == 204:
            current_app.db_session.commit()
        else:
            abort(404)

        return '', 204


class UmbrellaOrgMemberOrgAssociationsResource(restful.Resource):
    def get(self, umbrella_organisation_id):
        """
        Get member organisations of an umbrella organisation.

        :param umbrella_organisation_id: ID of umbrella organisation
        :statuscode 200: No error
        :statuscode 400: Missing umbrella organisation ID
        :statuscode 400: No member organisations found
        """
        if not umbrella_organisation_id:
            abort(400, __error__=["Paraplyorganisasjonsid mangler"])
        try:
            member_org_associations = current_app.db_session.query(UmbrellaOrgMemberOrgAssociation).filter(
                UmbrellaOrgMemberOrgAssociation.umbrella_organisation_id == umbrella_organisation_id
            ).join(UmbrellaOrgMemberOrgAssociation.organisation).order_by(Organisation.name).all()
        except NoResultFound:
            abort(
                400,
                __error__=[
                    "Fant ingen medlemsorganisajoner for paraplyorganisasjon med id=%s." % umbrella_organisation_id]
            )
        response = marshal(member_org_associations, umbrella_org_member_org_association_fields)
        return Response(json.dumps(response), 200, mimetype='application/json')

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def post(self, umbrella_organisation_id):
        """
        Create a new member organisation of an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/umbrella_organisations/123/organisations/ HTTP/1.1
           Content-Type: application/json

           {
               "organisation_id": 321
           }

        :param umbrella_organisation_id: ID of umbrella organisation
        :statuscode 201: No error
        :statuscode 400: Missing umbrella organisation ID
        :statuscode 400: Umbrella organisation does not exist
        :statuscode 400: Missing organisation ID
        :statuscode 400: Organisation does not exist
        :statuscode 400: Constraint violation
        :statuscode 401: Unauthorized
        """
        posted_data = request.get_json()
        organisation_id = posted_data.get('organisation_id', None)
        if not umbrella_organisation_id:
            abort(400, __error__=["Paraplyorganisasjonsid mangler"])
        try:
            umbrella_org = current_app.db_session.query(UmbrellaOrganisation).filter(
                UmbrellaOrganisation.id == umbrella_organisation_id
            ).one()
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen paraplyorganisasjon med id=%s." % umbrella_organisation_id]
            )
        if not organisation_id:
            abort(400, __error__=["Organisasjonsid mangler"])
        try:
            org = current_app.db_session.query(Organisation).filter(
                Organisation.id == organisation_id
            ).one()
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen organisasjon med id=%s." % organisation_id]
            )
        member_organisation = UmbrellaOrgMemberOrgAssociation(umbrella_org, org)
        try:
            current_app.db_session.add(member_organisation)
            current_app.db_session.commit()
            current_app.db_session.refresh(member_organisation)
            response = marshal(member_organisation, umbrella_org_member_org_association_fields)
            return Response(json.dumps(response), 201, mimetype='application/json')
        except Exception, err:
            abort(400,
                  __error__=["Kunne ikke oppdatere paraplyorganisasjon."]
                  )

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def delete(self, umbrella_organisation_id, association_id):
        """
        Delete a member organisation of an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           DELETE /api/v1/umbrella_organisations/123/organisations/321 HTTP/1.1

        :statuscode 204: No error
        :statuscode 400: Missing organisation ID
        :statuscode 400: Organisation does not exist
        :statuscode 401: Unauthorized
        """
        if not association_id:
            abort(400,
                  __error__=["Id mangler"]
                  )
        try:
            member_org_association = current_app.db_session.query(
                UmbrellaOrgMemberOrgAssociation
            ).get(association_id)
        except NoResultFound:
            abort(
                400,
                __error__=["Medlemsorganisjon ikke funnet med id=%s." % association_id]
            )
        current_app.db_session.delete(member_org_association)
        current_app.db_session.commit()
        return '', 204


class UmbrellaOrganisationResource(restful.Resource):
    def find_by_name(self, name):
        try:
            result = current_app.db_session.query(UmbrellaOrganisation).filter(
                UmbrellaOrganisation.name == name
            )
            return result.one()
        except NoResultFound:
            return None

    def get(self, umb_org_id=None, umb_org_name=None):
        """
        Get all umbrella organisations or by ID/name.

        :param umb_org_id: ID of umbrella organisation
        :param name: Name of umbrella organisation, overrides umb_org_id if both are given
        :param show_deleted: If True, include deleted organisations in response
        :param person_id: Only return organisations where person is a member
        :statuscode 200: No error
        :statuscode 404: Umbrella organisation does not exist
        """

        if umb_org_name:
            umb_org = self.find_by_name(umb_org_name)

            if umb_org:
                return marshal(
                    umb_org,
                    umbrella_organisation_fields
                ), 200
            else:
                return abort(404, __error__=[u'Det finnes ingen paraplyorganisasjon med navnet %s' % umb_org_name])

        else:
            umbrellas = current_app.db_session.query(UmbrellaOrganisation).order_by(
                UmbrellaOrganisation.name
            )
            if umb_org_id:
                umb_org = umbrellas.get(umb_org_id)
                if not umb_org:
                    abort(404)
                return marshal(
                    umb_org,
                    umbrella_organisation_fields
                ), 200
            else:
                # Add custom filters
                if 'show_deleted' not in request.args:
                    umbrellas = umbrellas.filter(UmbrellaOrganisation.is_deleted == False)

                if "person_id" in request.args:
                    umbrellas = umbrellas.filter(
                        UmbrellaOrganisation.persons.any(Person.id.in_([request.args["person_id"]]))
                    )

                return marshal(umbrellas.all(), umbrella_organisation_fields), 200

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def post(self):
        """
        Create an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/umbrella_organisations/123 HTTP/1.1
           Content-Type: application/json

           {
               "name": "My organisation"
           }

        :statuscode 201: No error
        :statuscode 400: Duplicate organisation name
        :statuscode 400: Missing organisation name
        :statuscode 401: Unauthorized
        """

        data = request.get_json()
        # get name!
        if not data:
            abort(400, __error__=[u'Manglende data for paraplyorganisasjon.'])

        mandatory_fields = [('name', 'Paraplyorganisasjonens navn')]
        parameters = {}
        for field, display_name in mandatory_fields:
            if field not in data or data.get(field).strip() == "":
                abort(400, __error__=["{0} må fylles ut".format(display_name)])
            parameters[field] = data[field]

        existing_umbrella_organisation_with_same_name = self.find_by_name(data.get('name'))
        if existing_umbrella_organisation_with_same_name:
            abort(400, __error__=[u'Det finnes allerede en paraplyorganisasjon med samme navn'])

        umbrella_org = UmbrellaOrganisation(**parameters)
        try:
            current_app.db_session.add(umbrella_org)
            current_app.db_session.commit()
            current_app.db_session.refresh(umbrella_org)

        except Exception as e:
            abort(400, __error__=[u'Kunne ikke lagre paraplyorganisasjon: %s' % e.message])

        response = marshal(umbrella_org, umbrella_organisation_fields)
        return Response(json.dumps(response), 201, mimetype='application/json')

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def put(self, umb_org_id):
        """
        Update an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           PUT /api/v1/umbrella_organisations/123 HTTP/1.1
           Content-Type: application/json

           {
               "name": "My organisation"
           }

        :param umb_org_id: ID of umbrella organisation
        :statuscode 200: No error
        :statuscode 400: Missing ID
        :statuscode 400: Organisation does not exist
        :statuscode 400: Duplicate organisation name
        :statuscode 400: Invalid organisation name
        :statuscode 401: Unauthorized
        """

        if not umb_org_id:
            abort(400, __error__=["Paraplyorganisasjonsid mangler"])
        try:
            umbrella_org = current_app.db_session.query(UmbrellaOrganisation).filter(
                UmbrellaOrganisation.id == umb_org_id
            ).one()
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen paraplyorganisasjon med id=%s." % umb_org_id]
            )

        posted_data = request.get_json()
        name = posted_data.get('name', None)

        if name and len(name.strip()) > 0:
            if umbrella_org.name != name:
                existing_umbrella_organisation_with_same_name = self.find_by_name(name)
                if existing_umbrella_organisation_with_same_name:
                    abort(400, __error__=[u'Det finnes allerede en paraplyorganisasjon med samme navn'])

            set_attribute(umbrella_org, 'name', posted_data)
        else:
            abort(
                400,
                __error__=["Ikke ett gyldig navn."]
            )

        try:
            current_app.db_session.commit()
            current_app.db_session.refresh(umbrella_org)

            response = marshal(umbrella_org, umbrella_organisation_fields)
            return Response(json.dumps(response), mimetype='application/json')

        except Exception:
            abort(400, __error__=["Kunne ikke oppdatere paraplyorganisasjon."])

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def delete(self, umb_org_id=None):
        """
        Delete an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           DELETE /api/v1/umbrella_organisations/123 HTTP/1.1

        :statuscode 204: No error
        :statuscode 400: Missing organisation ID
        :statuscode 400: Organisation does not exist
        :statuscode 401: Unauthorized
        """
        if not umb_org_id:
            abort(400, __error__=["Paraplyorganisasjonsid mangler"])
        try:
            umbrella_org = current_app.db_session.query(UmbrellaOrganisation).get(umb_org_id)
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen paraplyorganisasjon med id=%s." % umb_org_id]
            )

        umbrella_org.is_deleted = True
        current_app.db_session.commit()

        return '', 204


class UmbrellaOrganisationPersonsResource(restful.Resource):
    def find_umb_org(self, umb_org_id):
        if not umb_org_id:
            abort(400, __error__=[u'Paraplyorganisasjonsid mangler'])

        try:
            result = current_app.db_session.query(UmbrellaOrganisation).filter(
                UmbrellaOrganisation.id == umb_org_id
            )
            umb_org = result.one()
            return umb_org
        except Exception:
            abort(
                404,
                __error__=[u'Fant ingen paraplyorganisasjon med id=%s ' % umb_org_id]
            )

    def find_person(self, national_identity_number=None):
        if not national_identity_number:
            abort(400, __error__=[u'Fødselsnummer mangler'])

        try:
            result = current_app.db_session.query(Person). \
                filter(Person.national_identity_number == national_identity_number)
            return result.one()
        except NoResultFound:
            return None

    @UserIsCookieAuthenticatedValidator()
    def get(self, umb_org_id, person_id=None):
        """
        Get members (persons) of an umbrella organisation.

        :param umb_org_id: ID of umbrella organisation
        :statuscode 200: No error
        :statuscode 401: Unauthorized
        """
        umb_org = self.find_umb_org(umb_org_id)
        marshaled = marshal(umb_org.persons, person_fields)
        return Response(json.dumps(marshaled), mimetype='application/json')

    @marshal_with(person_fields)
    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def post(self, umb_org_id, person_id=None):
        """
        Create a new member (person) of an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           POST /api/v1/umbrella_organisations/123/persons/ HTTP/1.1
           Content-Type: application/json

           {
               "national_identity_number": "05058512345"
           }

        :param umbrella_organisation_id: ID of umbrella organisation
        :statuscode 201: No error
        :statuscode 400: Invalid national identity number
        :statuscode 409: Person is already a member
        :statuscode 401: Unauthorized
        """
        umb_org = self.find_umb_org(umb_org_id)

        data = request.get_json()

        nin = data.get('nin')
        person = self.find_person(nin)
        if person is None:
            if len(nin) != 11 or not nin.isdigit():
                abort(400, __error__=[u'Fødselsnummer må bestå av 11 siffer'])
            person = Person(nin)
            person.first_name = data.get('first_name')
            person.last_name = data.get('last_name')
            person.email_address = data.get('email_address')
            person.phone_number = data.get('phone_number')

            validator = BaseValidator(data)

            validator.validate_is_name("first_name", "Fornavn")
            validator.validate_is_name("last_name", "Etternavn")

            validator.validate_is_email("email_address", label="E-post", requires_value=False)
            validator.validate_is_norwegian_phone_number("phone_number", label="Telefonnummer", requires_value=False)

            if validator.has_errors():
                abort(400, __error__=validator.errors)

            current_app.db_session.add(person)
            current_app.db_session.commit()
        else:
            duplicate_person = next(
                (duplicate_person for duplicate_person in umb_org.persons if duplicate_person.id == person.id), None)
            if duplicate_person:
                abort(409, __error__=[(u'En person med dette fødselsnummeret er '
                                       u'allerede lagt til på organisasjonen')])

        umb_org.add_person(person)
        current_app.db_session.commit()

        return person, 201

    @OrValidator(UserHasAdminRoleValidator(), UserHasOrganisationAdminRoleValidator())
    def delete(self, umb_org_id, person_id=None):
        """
        Delete a member (person) of an umbrella organisation.

        **Example request**:

        .. sourcecode:: http

           DELETE /api/v1/umbrella_organisations/123/persons/321 HTTP/1.1

        :statuscode 204: No error
        :statuscode 401: Unauthorized
        :statuscode 404: Missing person ID
        :statuscode 404: Person is not associated with umbrella organisation
        """
        umb_org = self.find_umb_org(umb_org_id)

        if not person_id:
            data = request.get_json()
            if data:
                person_id = data.get('id')

        if not person_id:
            abort(404, __error__=[u'Mangler person-id.'])

        person = PersonResource.get_person(person_id)
        if person is None:
            abort(404, __error__=[u'Mangler person'])

        if person not in umb_org.persons:
            abort(
                404,
                __error__=[u'Personen med id=%s '
                           u'er ikke assosiert med paraplyorganisasjonen.' % person_id]
            )

        umb_org.persons.remove(person)
        current_app.db_session.commit()
        return "", 204


class BrregActivityCodeResource(restful.Resource):
    @marshal_with(brreg_activity_code_fields)
    def get(self):
        """
        Get Brreg activity codes.

        :statuscode 200: No error
        """
        return current_app.db_session.query(BrregActivityCode).order_by(
            BrregActivityCode.code
        ).all()


class FlodActivityTypeResource(restful.Resource):
    @marshal_with(flod_activity_type_fields)
    def get(self):
        """
        Get Flod activity types.

        :statuscode 200: No error
        """
        return current_app.db_session.query(FlodActivityType).order_by(
            FlodActivityType.id
        ).all()


class DistrictResource(restful.Resource):
    @marshal_with(district_fields)
    def get(self):
        districts = current_app.db_session.query(District)
        return districts.all()


class OrganisationInternalNotesResource(restful.Resource):
    def find_org(self, org_id):
        if not org_id:
            abort(400, __error__=['org_id mangler'])

        result = current_app.db_session.query(Organisation).filter(
            Organisation.id == org_id
        )
        try:
            org = result.one()
            return org
        except Exception:
            abort(404, __error__=['Fant ingen organisasjon med id=%s ' % org_id])

    def get_user_id(self):
        auth_token = request.cookies.get('auth_token', None)
        if not auth_token:
            return None, False

        if verify_superuser_auth_token(auth_token):
            return None, True

        username = unsign_auth_token(auth_token)
        return username

    @OrValidator(UserHasOrganisationAdminRoleValidator(), UserHasAdminRoleValidator())
    @marshal_with(organisation_internal_note_fields)
    def get(self, organisation_id=None, note_id=None):
        if note_id is not None:
            note = current_app.db_session.query(
                OrganisationInternalNote
            ).get(note_id)
            if note is None:
                abort(404)
            return note
        else:
            notes = current_app.db_session.query(
                OrganisationInternalNote
            ).filter(OrganisationInternalNote.organisation_id == organisation_id)

            return notes.all()

    @OrValidator(UserHasOrganisationAdminRoleValidator(),
                 UserHasAdminRoleValidator())
    @marshal_with(organisation_internal_note_fields)
    def post(self, organisation_id=None):
        data = request.get_json()

        text = data["text"]

        organisation = self.find_org(organisation_id)

        auth_id = self.get_user_id()

        note = OrganisationInternalNote(organisation, text, auth_id)

        current_app.db_session.add(note)
        current_app.db_session.commit()
        current_app.db_session.refresh(note)

        return note, 201

    @OrValidator(UserHasOrganisationAdminRoleValidator(),
                 UserHasAdminRoleValidator())
    @marshal_with(organisation_internal_note_fields)
    def delete(self, organisation_id=None, note_id=None):
        if note_id is None:
            abort(400)
        note = current_app.db_session.query(
            OrganisationInternalNote
        ).get(note_id)
        if note is None:
            abort(404)

        current_app.db_session.delete(note)
        current_app.db_session.commit()

        return '', 204
