#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.restful import fields,  marshal, abort
from domain.models import Application
from BaseResource import (ISO8601DateTime, get_resource_from_web, get_organisation_from_web, get_person_from_web)
from common_fields import person_fields, organisation_fields
from celery_tasks.email_tasks import send_email_task
from util.email import format_repeating_slot_for_email, format_slot_for_email
from BaseApplicationResource import BaseApplicationResource
from sqlalchemy.orm.exc import NoResultFound

generic_slot_fields = {
    'id': fields.Integer,
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
}

resource_fields = {
    'name': fields.String,
    'unit_email_address': fields.String
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

class ArrangementBaseResource(BaseApplicationResource):
    t = Application
    type_name = "application"

    def get_affected_applications(self, arrangement):
        affected_applications = []
        for slot in arrangement.slots:

            start_date = slot.start_time.date()
            end_date = slot.end_time.date()
            week_day = slot.start_time.isoweekday()
            start_time = slot.start_time.time()
            end_time = slot.end_time.time()

            # Find all affected repeating applications
            repeating_slots = self.get_repeating_slots(arrangement.resource, start_date, end_date, week_day, start_time, end_time)
            for repeating_slot in repeating_slots:
                if repeating_slot.application not in affected_applications:
                    affected_applications.append(repeating_slot.application)

            # Find all affected single applications (except the arrangement itself)
            single_slots = self.get_slots(arrangement.resource, start_date, end_date, week_day, start_time, end_time)
            for single_slot in single_slots:
                if single_slot.application not in affected_applications and single_slot.application.id is not arrangement.id:
                    affected_applications.append(single_slot.application)

        return affected_applications

    def get_arrangement(self, application_id):
        try:
            application = self.get_object_by_id(application_id)
        except NoResultFound:
            abort(
                400,
                __error__=["Fant ingen søknad med id=%s." % application_id]
            )
        if not application.is_arrangement:
            abort(
                400,
                __error__=["Søknaden er ikke ett arrangement id=%s." % application_id]
            )
        return application
