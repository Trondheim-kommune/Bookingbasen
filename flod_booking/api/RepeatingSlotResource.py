# -*- coding: utf-8 -*-

from flask.ext import restful
from flask import current_app, request
from flask.ext.restful import fields, marshal_with, marshal
from flask.ext.bouncer import requires, ensure, PUT
from sqlalchemy import and_, or_, tuple_
from isodate import parse_date, parse_time

from api_exceptions import format_exception
from BaseResource import get_person_for_uri, \
    get_organisation_for_uri, ISO8601DateTime, \
    get_resource_for_uri, get_application_for_id
from domain.models import RepeatingSlot, Application
from BaseApplicationResource import BaseApplicationResource

repeating_slot_fields = {
    'id': fields.Integer,
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
}

class RepeatingDateResource(BaseApplicationResource):

    @classmethod
    def objects_containing_date(cls, objects, target_date):
        return objects.filter(and_(cls.t.start_date < target_date, cls.t.end_date > target_date))

    @classmethod
    def objects_overlapping_dates(cls, objects, start_date, end_date):
        return objects.filter(or_(cls.t.start_date.between(start_date, end_date),
            cls.t.end_date.between(start_date, end_date)))

    @classmethod
    def objects_unioning_dates(cls, objects, start_date, end_date):
        return objects.filter(or_(
            tuple_(
                cls.t.start_date, cls.t.end_date
            ).op('overlaps')(
                tuple_(
                    start_date, end_date
                )
            ),
            or_(
                # First range ends on the start date of the second
                cls.t.end_date == start_date,
                # Second range ends on the start date of the first
                end_date == cls.t.start_date
            )
        ))

    @classmethod
    def get_objects(cls, resource_id=None, resource_uri=None, request=None, union=False):

        # Verify that the resource exists
        resource = cls.get_resource_with_id_or_uri(resource_id, resource_uri)
        query = current_app.db_session.query(cls.t)
        # BlockedTime has resource directly, but slots dont
        if hasattr(cls.t, "resource"):
            objects = query.filter(cls.t.resource == resource)
        else:
            objects = query.filter(Application.resource == resource,
                                   cls.t.application_id == Application.id)

        if "date" in request.args:
            target_date = cls.parse_date_from_args(request.args, "date")
            objects = cls.objects_containing_date(objects, target_date)

        if "start_date" in request.args:
            start_date, end_date = cls.parse_date_range_from_args(request)
            if union:
                objects = cls.objects_unioning_dates(objects, start_date, end_date)
            else:
                objects = cls.objects_overlapping_dates(objects, start_date, end_date)

        return objects
