#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery_tasks.email_tasks import send_email_task
from domain.models import Application
from flask import render_template, request
from flask.ext.bouncer import requires, POST
from flask.ext.restful import fields, marshal
from util.email import format_repeating_slot_for_email, format_slot_for_email

from ArrangementBaseResource import ArrangementBaseResource
from BaseResource import (ISO8601DateTime, get_resource_from_web, get_organisation_from_web, get_person_from_web)
from common_fields import person_fields, organisation_fields

generic_slot_fields = {
    'id': fields.Integer,
    'start_date': ISO8601DateTime,
    'end_date': ISO8601DateTime,
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,
}

resource_fields = {
    'name': fields.String,
    'unit_email_address': fields.String
}

application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(generic_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'type': fields.String
}


class ArrangementNotificationResource(ArrangementBaseResource):
    t = Application
    type_name = "application"

    def send_email_to_affected_applications(self, arrangement,
                                            affected_applications,
                                            message):
        arrangement_slots = []
        for arrangement_slot in arrangement.slots:
            arrangement_slots.append(format_slot_for_email(arrangement_slot))

        for affected_application in affected_applications:
            if affected_application.slots:
                resource_details = get_resource_from_web(affected_application.resource.uri)
                resource_name = resource_details['name']

                person_details = get_person_from_web(affected_application.person.uri)
                email_address = person_details['email_address']

                org_name = None
                if affected_application.organisation is not None:
                    org_details = get_organisation_from_web(affected_application.organisation.uri)
                    org_name = org_details.get('name')

                application_time = affected_application.application_time.strftime("%Y.%m.%d %H:%M:00")

                slots = []
                # Just create human readable text out of slots
                for slot in affected_application.slots:
                    if affected_application.get_type() == "repeating":
                        slots.append(format_repeating_slot_for_email(slot))
                    else:
                        slots.append(format_slot_for_email(slot))

                msg = render_template("email_arrangement_notification.txt",
                                      org_name=org_name,
                                      resource_name=resource_name,
                                      application_time=application_time,
                                      slots=slots,
                                      arrangement_slots=arrangement_slots,
                                      message=message)

                if email_address and msg is not None:
                    send_email_task.delay(u'Arrangement',
                                          u'booking@trondheim.kommune.no',
                                          [email_address],
                                          msg)

    @requires(POST, 'ArrangementNotification')
    def post(self, application_id):
        data = request.get_json()
        message = data.get('message', '')
        arrangement = self.get_arrangement(application_id)
        affected_applications = self.get_affected_applications(arrangement)
        if len(affected_applications) > 0:
            self.send_email_to_affected_applications(arrangement,
                                                     affected_applications,
                                                     message)
        return marshal(affected_applications, application_fields)
