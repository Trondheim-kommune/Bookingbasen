from flask.ext import restful
from flask import current_app, request
from flask.ext.restful import fields, marshal_with, marshal, abort
from flask.ext.bouncer import requires, ensure, PUT, DELETE
from datetime import datetime
from isodate import parse_datetime
from sqlalchemy.orm.exc import NoResultFound

from domain.models import Slot, Application
from api_exceptions import format_exception
from BaseResource import BaseResource, get_person_for_uri, \
    get_organisation_for_uri, ISO8601DateTime, get_application_for_id


class DateBasedResource(BaseResource):
    @classmethod
    def objects_between_dates(cls, objects, start_date, end_date):

        objects = objects.filter(cls.t.start_time.between(datetime(start_date.year,
            start_date.month,
            start_date.day, 0),
            datetime(end_date.year,
                end_date.month,
                end_date.day, 23, 59, 59)))
        return objects

    @classmethod
    def get_objects(cls, resource_id=None, resource_uri=None, request=None):

        # Verify that the resource exists
        resource = cls.get_resource_with_id_or_uri(resource_id, resource_uri)
        query = current_app.db_session.query(cls.t)
        objects = query.filter(Application.resource == resource,
                               cls.t.application_id == Application.id)
        if "date" in request.args:
            target_date = cls.parse_date_from_args(request.args, "date")
            objects = cls.objects_between_dates(objects, target_date, target_date)

        if "start_date" in request.args:
            start_date, end_date = cls.parse_date_range_from_args(request)
            objects = cls.objects_between_dates(objects, start_date, end_date)

        return objects

slot_fields = {
    'id': fields.Integer,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    #'resource' : fields.Nested(resource_fields),
    #'person' : fields.Nested(person_fields),
    #'organisation' : fields.Nested(organisation_fields),
}

