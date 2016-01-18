#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.restful import fields,  marshal, abort
from flask.ext.bouncer import requires, GET
from domain.models import Application
from BaseResource import (ISO8601DateTime, get_resource_from_web, get_organisation_from_web, get_person_from_web)
from common_fields import person_fields, organisation_fields
from celery_tasks.email_tasks import send_email_task
from util.email import format_repeating_slot_for_email, format_slot_for_email
from ArrangementBaseResource import ArrangementBaseResource
from sqlalchemy.orm.exc import NoResultFound
from ResourceResource import resource_fields

generic_slot_fields = {
    'id': fields.Integer,
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
}

application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'person' : fields.Nested(person_fields),
    'organisation' : fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(generic_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'type': fields.String
}

class ArrangementConflictsResource(ArrangementBaseResource):
    t = Application
    type_name = "application"

    @requires(GET, 'ArrangementConflict')
    def get(self, application_id = None):
        arrangement = self.get_arrangement(application_id)
        return marshal(self.get_affected_applications(arrangement), application_fields)
