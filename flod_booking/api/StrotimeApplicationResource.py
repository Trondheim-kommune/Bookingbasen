#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from api.BaseApplicationResource import nearest_hour
from celery_tasks.email_tasks import send_email_task
from datetime import datetime
from domain.models import StrotimeSlot, Application
from flask import current_app, request, render_template
from flask.ext.bouncer import requires, ensure, POST, DELETE
from flask.ext.restful import marshal_with, abort
from isodate import parse_datetime
from util.email import format_slot_for_email, format_application_status_for_email

from BaseApplicationResource import BaseApplicationResource
from BaseResource import get_resource_for_uri, \
    get_person_for_uri, get_resource_from_web, get_person_from_web
from SettingsResource import SettingsResource
from application_fields import strotimer_application_fields
from email import send_email_to_resource

USERS_URL = os.environ.get('USERS_URL', 'http://localhost:4000')


def send_email_strotime_granted(application):
    person = get_person_from_web(application.person.uri)
    resource = get_resource_from_web(application.resource.uri)
    person_name = ''
    if person['first_name'] and person['last_name']:
        person_name = person['first_name'] + " " + person['last_name']
    if person['email_address']:
        application_status = format_application_status_for_email(application.status)

        resource_name = ""
        if resource['name']:
            resource_name = resource['name']

        slots = []
        for slot in application.slots:
            slots.append(format_slot_for_email(slot))
        message = render_template(
            "email_strotime_granted.txt",
            resource_name=resource_name,
            application_status=application_status,
            slots=slots,
            person_name=person_name
        )
        resource_email = person['email_address']
        if message is not None and resource_email is not None:
            send_email_task.delay(
                u'Strøtime tildelt',
                u'booking@trondheim.kommune.no',
                [resource_email],
                message
            )


class StrotimeApplicationResource(BaseApplicationResource):
    t = Application
    type_name = "application"

    def parse_slot_request(self, data, application):
        start_time = parse_datetime(data["start_time"])
        end_time = parse_datetime(data["end_time"])
        return StrotimeSlot(start_time, end_time, application)

    @requires(POST, Application)
    @marshal_with(strotimer_application_fields)
    def post(self):
        data = request.get_json()

        person_uri = data["person"]["uri"]
        text = data["text"]

        resource_uri = data["resource"]["uri"]
        resource = get_resource_for_uri(resource_uri)

        settings = SettingsResource().get()

        if not (resource.auto_approval_allowed and settings["strotime_booking_allowed"]):
            abort(403, __error__=[u'Strøtimer ikke tillatt'])

        person = get_person_for_uri(person_uri)
        application = Application(person, None, text, None, resource)

        datetime_now = datetime.now()

        slots = [self.parse_slot_request(d, application)
                 for d in data["slots"]]

        for slot in slots:
            start_date = slot.start_time.date()
            end_date = slot.end_time.date()
            week_day = slot.start_time.isoweekday()
            start_time = slot.start_time.time()
            end_time = slot.end_time.time()
            self.validate_start_and_end_times(start_date, end_date, start_time, end_time)

            if slot.start_time < nearest_hour(datetime_now):
                abort(400, __error__=[u'Du kan ikke søke om en time tilbake i tid'])

            if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time):
                abort(400, __error__=[u'Tiden du har søkt på er ikke tilgjengelig'])
            if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
                abort(400, __error__=[u'Tiden du har søkt på er blokkert'])

            # The start time must be in the range 3-21 days (inclusive)
            days = (slot.start_time.date() - datetime_now.date()).days
            if 3 <= days <= 21:
                application.add_strotime_slot(slot)
            else:
                abort(400, __error__=[u'Tiden må være innenfor 3-21 dager fra dagens dato'])

        application.status = 'Granted'
        current_app.db_session.add(application)
        current_app.db_session.commit()
        current_app.db_session.refresh(application)

        send_email_strotime_granted(application)
        send_email_to_resource(application)

        return application, 201

    @requires(DELETE, Application)
    def delete(self, application_id):
        application = self.get_object_by_id(application_id)

        if not application:
            abort(404)

        if application.type != 'strotime':
            abort(405)

        ensure(DELETE, application)

        for slot in application.strotime_slots:
            current_app.db_session.delete(slot)

        current_app.db_session.delete(application)
        current_app.db_session.commit()
        return "", 204
