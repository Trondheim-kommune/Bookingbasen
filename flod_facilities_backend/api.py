#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import os
from flask import current_app, Response, request, send_from_directory, render_template
from flask.ext import restful
from flask.ext.restful import abort, fields, marshal, marshal_with
from shapely.geometry import box, Point, mapping
from sqlalchemy.orm.exc import NoResultFound
from geoalchemy2.shape import from_shape
from sqlalchemy import or_
from domain.models import (ContactPerson, Document, Facility, FacilityType,
                           Image, UnitType, District, FacilityInternalNote)
from domain.storage import get_backend, get_backend_for_model, uuid_with_ext
from domain.images import images, remove_thumbnails
from flodapi import FlodApi
from validation.authentication_validators import UserIsCookieAuthenticatedValidator
from validation.credential_validators import CanEditFacilityValidator, CanCreateFacilityValidator
from validation.base_validators import AndValidator, OrValidator
import repo
from validation.role_validators import (UserHasAdminRoleValidator,
                                        UserRoleValidator)
from celery_app import celery_app


class ISO8601DateTime(fields.Raw):
    def format(self, value):
        return value.isoformat()


class Position(fields.Raw):
    def format(self, point):
        return {'lon': point.x, 'lat': point.y}


contact_person_fields = {
    'name': fields.String,
    'phone_number': fields.String
}

contact_person_fields_admin = {
    'name': fields.String,
    'phone_number': fields.String,
    'email': fields.String
}

image_fields = {
    'id': fields.Integer,
    'facility_id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'filename': fields.String
}

document_fields = {
    'id': fields.Integer,
    'facility_id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'filename': fields.String
}

id_name_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class GeometryItem(fields.Raw):
    def format(self, value):
        return mapping(value)


district_with_geom_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'geometry': GeometryItem
}


class DistrictItem(fields.Raw):
    def format(self, value):
        if not value:
            return None
        return marshal(value, id_name_fields)


facility_fields = {
    'id': fields.Raw,
    'uri': fields.String,
    'name': fields.String,
    'position': Position,
    'images': fields.Nested(image_fields),
    'documents': fields.Nested(document_fields),
    'short_description': fields.String,
    'link': fields.String,
    'description': fields.String,
    'webpage': fields.String,
    'contact_person': fields.Nested(contact_person_fields),
    'facility_type': fields.Nested(id_name_fields),
    'capacity': fields.Integer,
    'short_code': fields.String,
    'unit_number': fields.String,
    'floor': fields.String,
    'room': fields.String,
    'area': fields.Integer,
    'conditions': fields.String,
    'unit_name': fields.String,
    'unit_phone_number': fields.String,
    'unit_email_address': fields.String,
    'unit_leader_name': fields.String,
    'address': fields.String,
    'department_name': fields.String,
    'unit_type': fields.Nested(id_name_fields),
    'amenities': fields.Raw,
    'accessibility': fields.Raw,
    'suitability': fields.Raw,
    'equipment': fields.Raw,
    'facilitators': fields.Raw,
    'district': DistrictItem,
    'is_deleted': fields.Boolean,
    'is_published': fields.Boolean
}


# Include certain fields for admin users
replace_fields_admin = {'contact_person': fields.Nested(contact_person_fields_admin)}
facility_fields_admin = dict(facility_fields.items() + replace_fields_admin.items())

facility_internal_note_fields = {
    'id': fields.Integer,
    'auth_id': fields.String,
    'facility': fields.Nested(facility_fields_admin),
    'text': fields.String,
    'create_time': ISO8601DateTime,
}

API_VERSION = 'v1'


def bbox_to_polygon(bbox):
    bbox = [float(x) for x in bbox.split(',')]
    poly = box(*bbox, ccw=False)
    return poly.wkt


def parse_contact_person(data):
    name = data['contact_person']['name']
    optional = {
        "phone_number": data['contact_person'].get('phone_number', None)
    }
    phone_number = optional['phone_number']
    if phone_number and not phone_number.isdigit():
        abort(400, contact_person={'phone_number': 'must be all digits'})
    return ContactPerson(name, **optional)


def parse_facility_type(data):
    facility_types = current_app.db_session.query(FacilityType)
    facility_types = facility_types.filter(
        FacilityType.id == int(data['facility_type']["id"]))
    try:
        return facility_types.one()
    except NoResultFound:
        abort(400, facility_type={"id": 'The specified id does not exist.'})


def parse_unit_type(data):
    unit_types = current_app.db_session.query(UnitType)
    unit_types = unit_types.filter(
        UnitType.id == int(data['unit_type']["id"]))
    try:
        return unit_types.one()
    except NoResultFound:
        abort(400, unit_type={"id": 'The specified id does not exist.'})


def parse_optional_parameters(data):
    optional_parameters = [
        'unit_number', 'short_description', 'description', 'link',
        'short_code', 'webpage', 'floor', 'room', 'capacity',
        'area', 'conditions', 'department_name',
        'unit_name', 'unit_leader_name',
        'unit_phone_number', 'unit_email_address', 'address']

    optional = {}
    for parameter_name in optional_parameters:
        optional[parameter_name] = data.get(parameter_name, None)
    phone_number = optional['unit_phone_number']
    if phone_number and not phone_number.isdigit():
        abort(400, unit_phone_number='must be all digits')
    return optional


def parse_position(data):
    if data.get('position', None):
        lat = data['position']['lat']
        lon = data['position']['lon']
        return Point(lon, lat)


def parse_dict(data, name):
    dct = {}
    if name in data:
        dct = data[name]
    return dct


class FacilityResource(restful.Resource):
    def get(self):

        if 'name' in request.args and request.args['name'] == '':
            return marshal([], facility_fields)

        facilities = current_app.db_session.query(Facility).order_by(Facility.name.asc())

        max_capacity = None
        min_capacity = None
        if 'name' in request.args:
            name_filter = Facility.name.ilike('%%%s%%' % request.args['name'])
            short_code_filter = Facility.short_code.ilike(
                '%s' % request.args['name'])
            facilities = facilities.filter(or_(name_filter, short_code_filter))
        if 'bbox' in request.args:
            facilities = facilities.filter(
                Facility.pos.contained(bbox_to_polygon(request.args['bbox'])))
        if 'district' in request.args:
            facilities = facilities.filter(
                Facility.district_id == request.args['district'])
        if 'min_capacity' in request.args:
            try:
                min_capacity = int(request.args['min_capacity'])
                facilities = facilities.filter(
                    Facility.capacity >= min_capacity)
            except ValueError:
                abort(400, min_capacity='must be a valid integer')
        if 'max_capacity' in request.args:
            try:
                max_capacity = int(request.args['max_capacity'])
                facilities = facilities.filter(
                    Facility.capacity <= max_capacity)
            except ValueError:
                abort(400, max_capacity='must be a valid integer')
        if max_capacity and min_capacity and min_capacity > max_capacity:
            abort(400, max_capacity=('max_capacity must be greater than '
                                     'min_capacity'))

        if 'short_code' in request.args:
            facilities = facilities.filter(
                Facility.short_code == request.args['short_code'])

        if 'type' in request.args:
            try:
                type_id = int(request.args['type'])
                facilities = facilities.filter(
                    Facility.facility_type_id == type_id)
            except ValueError:
                abort(400, type='type must integer')

        if 'accessibility' in request.args:
            accessibility = request.args["accessibility"]
            keys = accessibility.split(",")
            facilities = facilities.filter(Facility.accessibility.has_all(keys))

        anonymous = False
        user = {}
        superuser = repo.is_super_admin(request.cookies)
        if not superuser:
            user = repo.get_user(request.cookies)
            anonymous = user is None

        # Do not show deleted facilities by default
        show_deleted = request.args.get('show_deleted', False)
        if not show_deleted:
            facilities = facilities.filter(Facility.is_deleted == False)

        # Do not show not published facilities by default
        show_not_published = request.args.get('show_not_published', False)
        if not show_not_published:
            facilities = facilities.filter(Facility.is_published == True)

        # NOTE: Admin should see all facilities, regular AD users only to see their own
        if not anonymous and not superuser and repo.is_administrator(user):
            if 'show_only_my_facilities' in request.args and request.args['show_only_my_facilities'] == 'True':
                my_facilities = repo.get_facilities_edit_credentials(user['id'], request.cookies)
                facilities = facilities.filter(Facility.id.in_(my_facilities))

        facilities = facilities.all()
        if anonymous or not repo.is_administrator(user):
            return marshal(facilities, facility_fields)

        return marshal(facilities, facility_fields_admin)

    @OrValidator(UserHasAdminRoleValidator(),
                 AndValidator(CanCreateFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')))
    def post(self):
        data = request.get_json()
        name = data['name']

        optional = parse_optional_parameters(data)
        optional["position"] = parse_position(data)

        if optional["link"]:
            if not (len(optional["link"]) <= 200):
                abort(400, __error__=[u'Maks lengde for lenke er 200 tegn'])

            if not (optional["link"].strip().startswith('http://') or optional["link"].strip().startswith('https://')):
                abort(400, __error__=[u'Lenke må starte med http eller https'])

        if 'contact_person' in data:
            optional['contact_person'] = parse_contact_person(data)

        if 'facility_type' in data and 'id' in data['facility_type']:
            optional['facility_type'] = parse_facility_type(data)

        if 'unit_type' in data and 'id' in data['unit_type']:
            optional['unit_type'] = parse_unit_type(data)

        fac = Facility(name, **optional)
        fac.amenities = parse_dict(data, "amenities")
        fac.accessibility = parse_dict(data, "accessibility")
        fac.equipment = parse_dict(data, "equipment")
        fac.suitability = parse_dict(data, "suitability")
        fac.facilitators = parse_dict(data, "facilitators")

        if 'is_deleted' in data:
            fac.is_deleted = data['is_deleted']

        if 'is_published' in data:
            fac.is_published = data['is_published']

        current_app.db_session.add(fac)
        current_app.db_session.commit()
        current_app.db_session.refresh(fac)

        # Make sure the user who created the facility is allowed to edit it
        user_id = repo.get_user_id_for_user(cookies=request.cookies)
        if user_id:
            added_credentials = repo.add_edit_credentials(user_id, fac.id, request.cookies)
            if fac.id and added_credentials:
                return marshal(fac, facility_fields_admin), 201

            # If we were NOT successful all the way above, we have to delete the facility
            try:
                current_app.db_session.delete(fac)
                current_app.db_session.commit()
            except:
                current_app.logger.warn(
                    "Not able to delete facility#id " + str(fac.id) + ", after updating credentials failed.")
                pass

            abort(500, __error__=["Error creating facility."])
        else:
            return marshal(fac, facility_fields_admin), 201


class FacilityTypeResource(restful.Resource):
    @marshal_with(id_name_fields)
    def get(self):
        return current_app.db_session.query(FacilityType).all()


class UnitTypeResource(restful.Resource):
    @marshal_with(id_name_fields)
    def get(self):
        return current_app.db_session.query(UnitType).all()


class SingleFacilityResource(restful.Resource):
    def get_or_abort(self, facility_id):
        facilities = current_app.db_session.query(Facility)

        facility = facilities.get(facility_id)
        if not facility:
            abort(404)

        if facility.is_deleted:
            abort(404)

        return facility

    def get(self, facility_id):
        user = repo.get_user(request.cookies)
        anonymous = user is None

        facility = self.get_or_abort(facility_id)

        if anonymous or not repo.is_administrator(user):
            return marshal(facility, facility_fields)
        else:
            return marshal(facility, facility_fields_admin)

    @AndValidator(UserIsCookieAuthenticatedValidator())
    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def delete(self, facility_id=None):
        facility = self.get_or_abort(facility_id)

        # current_app.db_session.delete(facility)
        facility.is_deleted = True
        current_app.db_session.commit()

        return '', 204

    @marshal_with(facility_fields_admin)
    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def put(self, facility_id):

        facility = self.get_or_abort(facility_id)

        data = request.get_json()

        facility.name = data['name']

        optionals = parse_optional_parameters(data)
        if optionals["link"]:
            if not (len(optionals["link"]) <= 200):
                abort(400, __error__=[u'Maks lengde for lenke er 200 tegn'])
            if not (optionals["link"].strip().startswith('http://') or optionals["link"].strip().startswith('https://')):
                abort(400, __error__=[u'Lenke må starte med http eller https'])

        for key, value in optionals.iteritems():
            setattr(facility, key, value)

        if 'is_deleted' in data and data['is_deleted'] == True:
            facility.is_deleted = data['is_deleted']
            current_app.db_session.commit()
            current_app.db_session.refresh(facility)
            return '', 204

        if 'is_published' in data:
            facility.is_published = data['is_published']

        if 'contact_person' in data:
            facility.contact_person = parse_contact_person(data)

        if 'facility_type' in data and 'id' in data['facility_type']:
            facility.facility_type = parse_facility_type(data)

        if 'unit_type' in data and 'id' in data['unit_type']:
            facility.unit_type = parse_unit_type(data)

        facility.amenities = parse_dict(data, "amenities")
        facility.accessibility = parse_dict(data, "accessibility")
        facility.equipment = parse_dict(data, "equipment")
        facility.suitability = parse_dict(data, "suitability")
        facility.facilitators = parse_dict(data, "facilitators")

        position = parse_position(data)
        facility.set_position(position)
        if position:
            try:
                district = current_app.db_session.query(District). \
                    filter(District.geom.ST_Covers(from_shape(position, 4326)))
                facility.district = district.one()
            except NoResultFound:
                pass

        current_app.db_session.commit()
        current_app.db_session.refresh(facility)

        return facility, 200


def documents(filename):
    doc_path = os.environ.get('DOCUMENTS_PATH', '/tmp')
    return send_from_directory(doc_path, filename)


def abort_with_msg(data, status=400):
    abort(status, status=status, __error__=data)


class FacilityImageResource(restful.Resource):
    @marshal_with(image_fields)
    def get(self, image_id=None, **kwargs):
        if image_id is None:
            abort(400)
        image = current_app.db_session.query(Image).get(image_id)
        if image is None:
            abort(404)
        return image

    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def delete(self, image_id=None, **kwargs):
        if image_id is None:
            abort(400)
        image = current_app.db_session.query(Image).get(image_id)
        if image is None:
            abort(404)

        backend = get_backend_for_model(image, os.environ.get('IMAGES_PATH',
                                                              '/tmp'))
        if backend is None:
            current_app.logger.warn(('Could not delete associated file. '
                                     'Unknown backend for model: %s (id: %d)'), image, image.id)
        else:
            backend.delete()

        remove_thumbnails(image.filename)

        current_app.db_session.delete(image)
        current_app.db_session.commit()
        return '', 204


class FacilityImageListResource(restful.Resource):
    valid_mimetypes = ('image/gif', 'image/jpeg', 'image/png')

    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def post(self, **kwargs):
        facility_id = request.form.get('facilityId')
        if facility_id is None:
            abort(400)
        facility = current_app.db_session.query(Facility).get(facility_id)
        if facility is None:
            abort(404)

        errors = {}

        title = request.form.get('title')
        if title is None or len(title.strip()) == 0:
            current_app.logger.warn('Missing required field: title')
            errors['title'] = u'Tittel er påkrevd'
        elif len(title) > 50:
            errors['title'] = u'Tittel kan ikke være lengre enn 50 tegn'

        file = request.files.get('image')
        if file is None:
            current_app.logger.warn('Missing required file: image')
            errors['image'] = u'Bilde er påkrevd'
        elif file.mimetype not in FacilityImageListResource.valid_mimetypes:
            current_app.logger.warn('Invalid mimetype: %s', file.mimetype)
            errors['image'] = (u'Ugyldig filtype. Gyldige filetyper er '
                               u'JPG/GIF/PNG')

        if len(errors) != 0:
            abort_with_msg(errors)

        backend = get_backend(file, filename=uuid_with_ext(file.filename),
                              path=os.environ.get('IMAGES_PATH', '/tmp'))
        backend.save()

        image = Image(facility, url=backend.get_url('images'), title=title,
                      filename=backend.filename, storage_backend=backend.name)
        current_app.db_session.add(image)
        current_app.db_session.commit()

        current_app.db_session.refresh(image)

        return Response(response=json.dumps(marshal(image, image_fields)), status=201, content_type=content_type_from_request())


def content_type_from_request():
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        return 'application/json'
    else:
        return 'text/html'


class FacilityDocumentResource(restful.Resource):
    @marshal_with(document_fields)
    def get(self, document_id=None):
        if document_id is None:
            abort(400)
        document = current_app.db_session.query(Document).get(document_id)
        if document is None:
            abort(404)
        return document

    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def delete(self, document_id=None, **kwargs):
        if document_id is None:
            abort(400)
        document = current_app.db_session.query(Document).get(document_id)
        if document is None:
            abort(404)

        backend = get_backend_for_model(document,
                                        os.environ.get('DOCUMENTS_PATH',
                                                       '/tmp'))
        if backend is None:
            current_app.logger.warn(('Could not delete associated file. '
                                     'Unknown backend for model: %s (id: %d)'), document,
                                    document.id)
        else:
            backend.delete()

        current_app.db_session.delete(document)
        current_app.db_session.commit()
        return '', 204


class FacilityDocumentListResource(restful.Resource):
    valid_mimetypes = ('application/pdf', 'application/msword',
                       ('application/vnd.openxmlformats-officedocument'
                        '.wordprocessingml.document'))

    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def post(self, **kwargs):
        facility_id = request.form.get('facilityId')
        if facility_id is None:
            abort(400)

        facility = current_app.db_session.query(Facility).get(facility_id)
        if facility is None:
            abort(404)

        errors = {}

        title = request.form.get('title')
        if title is None or len(title.strip()) == 0:
            current_app.logger.warn('Missing required parameter: title')
            errors['title'] = u'Tittel er påkrevd'
        elif len(title) > 50:
            errors['title'] = u'Tittel kan ikke være lengre enn 50 tegn'

        file = request.files.get('document')
        if file is None:
            current_app.logger.warn('Missing required file: document')
            errors['file'] = u'Dokument er påkrevd'
        elif file.mimetype not in FacilityDocumentListResource.valid_mimetypes:
            current_app.logger.warn('Invalid mimetype: %s', file.mimetype)
            errors['document'] = (u'Ugyldig filtype. Gyldige filtyper er '
                                  u'PDF/DOC/DOCX')

        if len(errors) != 0:
            abort_with_msg(errors)

        backend = get_backend(file, filename=uuid_with_ext(file.filename),
                              path=os.environ.get('DOCUMENTS_PATH', '/tmp'))
        backend.save()

        document = Document(facility, url=backend.get_url('documents'),
                            title=title,
                            filename=backend.filename,
                            storage_backend=backend.name)
        current_app.db_session.add(document)
        current_app.db_session.commit()

        current_app.db_session.refresh(facility)

        return Response(response=json.dumps(marshal(document, document_fields)), status=201, content_type=content_type_from_request())


class DistrictResource(restful.Resource):
    @marshal_with(district_with_geom_fields)
    def get(self):
        districts = current_app.db_session.query(District)
        return districts.all()


class FacilityInternalNotesResource(restful.Resource):
    t = FacilityInternalNote
    type_name = "facilities_internal_notes"

    @marshal_with(facility_internal_note_fields)
    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def get(self, facility_id=None, note_id=None):
        if note_id is not None:
            note = current_app.db_session.query(FacilityInternalNote).get(note_id)
            if note is None:
                abort(404)
            return note
        else:
            notes = current_app.db_session.query(FacilityInternalNote).filter(FacilityInternalNote.facility_id == facility_id)
            return notes.all()

    @marshal_with(facility_internal_note_fields)
    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def post(self, facility_id=None, note_id=None):
        data = request.get_json()

        text = data["text"]

        facility_id = data["facility"]["id"]
        facilities = current_app.db_session.query(Facility)
        facility = facilities.get(facility_id)
        if not facility:
            abort(404)

        auth_id = data["auth_id"]

        note = FacilityInternalNote(facility, text, auth_id)

        if facility.unit_email_address:
            message = render_template("email_facility_note_added_template.txt",
                                      facility_name=facility.name,
                                      internal_note=text)

            celery_app.send_task('celery_tasks.email_tasks.send_email_task',
                                 (u'Notat lagt til på lokale',
                                  u'booking@trondheim.kommune.no',
                                  [facility.unit_email_address],
                                  message))

        current_app.db_session.add(note)
        current_app.db_session.commit()
        current_app.db_session.refresh(note)

        return note, 201

    @marshal_with(facility_internal_note_fields)
    @OrValidator(AndValidator(CanEditFacilityValidator(),
                              UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_brukere')),
                 AndValidator(UserIsCookieAuthenticatedValidator(),
                              UserRoleValidator('flod_lokaler_admin')))
    def delete(self, facility_id=None, note_id=None):
        if note_id is None:
            abort(400)
        note = current_app.db_session.query(FacilityInternalNote).get(note_id)
        if note is None:
            abort(404)

        current_app.db_session.delete(note)
        current_app.db_session.commit()

        return '', 204


def create_api(app, api_version):
    api = FlodApi(app)

    #
    # Actually setup the Api resource routing here
    #
    api.add_resource(FacilityResource, '/api/%s/facilities/' % API_VERSION)
    api.add_resource(SingleFacilityResource,
                     '/api/%s/facilities/<int:facility_id>' % API_VERSION)
    api.add_resource(FacilityTypeResource,
                     '/api/%s/facility_types/' % API_VERSION)
    api.add_resource(UnitTypeResource, '/api/%s/unit_types/' % API_VERSION)
    api.add_resource(FacilityImageResource,
                     '/api/{0}/images/<int:image_id>'.format(API_VERSION))
    api.add_resource(FacilityImageListResource,
                     '/api/{0}/images/'.format(API_VERSION))
    api.add_resource(FacilityDocumentResource,
                     '/api/{0}/documents/<int:document_id>'.format(
                         API_VERSION)),
    api.add_resource(FacilityDocumentListResource,
                     '/api/{0}/documents/'.format(API_VERSION))
    api.add_resource(DistrictResource, '/api/%s/districts/' % API_VERSION)
    api.add_resource(FacilityInternalNotesResource,
                     '/api/%s/facilities/<int:facility_id>/notes/<int:note_id>' % api_version,
                     '/api/%s/facilities/<int:facility_id>/notes/' % api_version)
    app.add_url_rule('/media/facilities/documents/<filename>', 'documents',
                     documents)
    app.add_url_rule('/media/facilities/documents/<path:filename>',
                     'documents', documents)
    app.add_url_rule('/media/facilities/images/<path:filename>', 'images',
                     images)
    return app
