#!/usr/bin/env python
# -*- coding: utf-8 -*-
from domain.models import SlotRequest, Application
from flask import current_app, request
from flask.ext.bouncer import requires, POST
from flask.ext.restful import marshal_with, abort
from isodate import parse_datetime
from repo import get_user, has_role

from BaseApplicationResource import BaseApplicationResource
from BaseResource import get_resource_for_uri, \
    get_organisation_for_uri, get_person_for_uri
from SettingsResource import SettingsResource
from application_fields import single_application_fields
from email import send_email_to_resource, send_email_to_applicant


class SingleApplicationResource(BaseApplicationResource):
    def parse_slot_request(self, data):
        start_time = parse_datetime(data["start_time"])
        end_time = parse_datetime(data["end_time"])
        return SlotRequest(start_time, end_time)

    @requires(POST, Application)
    @marshal_with(single_application_fields)
    def post(self):
        data = request.get_json()

        is_arrangement = data.get("isArrangement", False)
        person = data.get('person', None)
        if not person or not person.get('uri', None):
            abort(400)
        person_uri = person["uri"]
        text = data["text"]
        facilitation = data["facilitation"]

        resource_uri = data["resource"]["uri"]
        resource = get_resource_for_uri(resource_uri)

        settings = SettingsResource().get()
        user = get_user(request.cookies)

        # Check that the resource allows the type of application
        if not (has_role(user, 'flod_saksbehandlere') and is_arrangement):
            if not settings["single_booking_allowed"] and not (has_role(user, 'flod_brukere') or has_role(user, 'flod_saksbehandlere')) or \
                    not resource.single_booking_allowed:
                abort(403, __error__=[u'Engangslån ikke tillatt'])

        organisation_data = data.get("organisation", None)
        if organisation_data:
            organisation_uri = organisation_data["uri"]
            organisation = get_organisation_for_uri(organisation_uri)
        else:
            organisation = None

        person = get_person_for_uri(person_uri)
        application = Application(
            person,
            organisation,
            text,
            facilitation,
            resource,
            amenities=data.get('amenities'),
            accessibility=data.get('accessibility'),
            equipment=data.get('equipment'),
            suitability=data.get('suitability'),
            facilitators=data.get('facilitators')
        )
        application.is_arrangement = is_arrangement

        slots = [self.parse_slot_request(d) for d in data["slots"]]
        if not slots:
            abort(400, __error__=[u'Tidspunkt mangler'])

        for slot in slots:
            start_date = slot.start_time.date()
            end_date = slot.end_time.date()
            week_day = slot.start_time.isoweekday()
            start_time = slot.start_time.time()
            end_time = slot.end_time.time()

            self.validate_end_date_of_slot(settings["single_booking_enddate"], end_date.isoformat(), u'engangslån')
            self.validate_start_and_end_times(start_date, end_date, start_time, end_time)

            if not is_arrangement:
                if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time) or \
                        self.is_conflict_rammetid(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(
                        400,
                        __error__=[u'Tiden du har søkt på er ikke tilgjengelig']
                    )

            if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
                abort(
                    400,
                    __error__=[u'Tiden du har søkt på er blokkert']
                )

            application.request_single_slot(slot)

        current_app.db_session.add(application)
        current_app.db_session.commit()
        current_app.db_session.refresh(application)
        send_email_to_resource(application)
        send_email_to_applicant(application)
        return application, 201
