#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import current_app, request
from flask.ext.restful import abort, fields, marshal_with
from flask.ext.bouncer import requires, ensure, POST
from domain.models import Application, RepeatingSlot, RepeatingSlotRequest, RammetidSlot, Rammetid
from BaseResource import get_resource_for_uri, get_organisation_for_uri, get_person_for_uri, ISO8601DateTime, get_umbrella_organisation_for_uri, get_umbrella_organisation_from_web
from BaseApplicationResource import BaseApplicationResource
from flod_common.session.utils import make_superuser_auth_cookie
from repo import get_user
from RammetidToApplication import RammetidToApplication
from util.merge import merge
from isodate import parse_date, parse_time
from sqlalchemy import Date, cast
from common_fields import person_fields, organisation_fields
from ResourceResource import resource_fields
from RepeatingSlotResource import repeating_slot_fields

repeating_application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'facilitation': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(repeating_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime
}


class RammetidToApplicationResource(BaseApplicationResource):
    def parse_slot(self, data, application):
        start_date = parse_date(data["start_date"])
        end_date = parse_date(data["end_date"])
        start_time = parse_time(data["start_time"])
        end_time = parse_time(data["end_time"])
        week_day = data["week_day"]
        return RepeatingSlot(
            application,
            week_day,
            start_date,
            end_date,
            start_time,
            end_time
        )

    def parse_slot_request(self, data):
        start_date = parse_date(data["start_date"])
        end_date = parse_date(data["end_date"])
        start_time = parse_time(data["start_time"])
        end_time = parse_time(data["end_time"])
        week_day = data["week_day"]
        return RepeatingSlotRequest(
            week_day,
            start_date,
            end_date,
            start_time,
            end_time
        )

    def has_matching_rammetid(self, umbrella_org_id, start_date, end_date, week_day, start_time, end_time):
        times = []

        query = current_app.db_session.query(RammetidSlot)
        slots = query.filter(
            RammetidSlot.start_date <= cast(start_date, Date),
            RammetidSlot.end_date >= cast(end_date, Date),
            week_day == RammetidSlot.week_day,
            umbrella_org_id == Rammetid.umbrella_organisation_id,
        ).order_by(RammetidSlot.start_time, RammetidSlot.end_time).all()

        # create list of time-periods for all slots
        for slot in slots:
            times.append((slot.start_time, slot.end_time))

        # return if any merged slot covers whole time-period
        if any(i[0] <= start_time and i[1] >= end_time for i in merge(times)):
            return True

        return False

    @requires(POST, RammetidToApplication)
    @marshal_with(repeating_application_fields)
    def post(self):
        data = request.get_json()

        rammetid_to_application = RammetidToApplication(data.get('umbrella_organisation').get('uri'))
        ensure(POST, rammetid_to_application)

        resource = data.get("resource", None)
        if not resource:
            abort(403, __error__=[u'Ressurs er ikke angitt.'])

        resource = get_resource_for_uri(resource['uri'])
        if not resource:
            abort(404, __error__=[u'Ressursen finnes ikke.'])

        if not resource.repeating_booking_allowed:
            abort(403, __error__=[u'Gjentakende lån ikke tillatt'])

        user = get_user(request.cookies)
        person_uri = '/persons/{}'.format(user['person_id'])
        person = get_person_for_uri(person_uri)
        if not person:
            abort(404, __error__=[u'Personen finnes ikke.'])

        # get umbrella member orgs from organisations backend
        umbrella_member_organisations = get_umbrella_organisation_from_web(data.get('umbrella_organisation').get('uri')).get('organisations', [])

        # get local umbrella organisation object
        umbrella_organisation = get_umbrella_organisation_for_uri(data.get('umbrella_organisation').get('uri'))

        text = "Rammetid fordeling"

        applications = []
        organisations = data.get('organisations', None)
        for organisation in organisations:
            organisation_data = organisations[organisation]
            # have to be superuser if the organisation is not public and not copied to booking already
            organisation = get_organisation_for_uri(organisation_data['uri'], cookies=make_superuser_auth_cookie())

            if not organisation:
                abort(404, __error__=[u'Organisasjonen finnes ikke.'])

            if not any(org.get('uri') == organisation_data['uri'] for org in umbrella_member_organisations):
                abort(403, __error__=[u'Organisasjonen hører ikke til paraplyorganisasjonen'])

            application = Application(person, organisation, text, None, resource)
            application.status = 'Granted'

            slots = organisation_data["slots"]
            for slot_data in slots:

                slot = self.parse_slot(slot_data, application)
                slot_request = self.parse_slot_request(slot_data)

                start_date = slot.start_date
                end_date = slot.end_date
                week_day = slot.week_day
                start_time = slot.start_time
                end_time = slot.end_time

                self.validate_start_and_end_times(start_date, end_date, start_time, end_time)

                if not self.has_matching_rammetid(umbrella_organisation.id, start_date, end_date, week_day, start_time, end_time):
                    abort(400, __error__=[u'Ingen rammetid passer'])

                if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(400, __error__=[u'Tiden du har søkt på er ikke tilgjengelig'])

                if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(400, __error__=[u'Tiden du har søkt på er blokkert'])

                application.request_repeating_slot(slot_request)
                application.add_repeating_slot(slot)
            applications.append(application)

        for application in applications:
            current_app.db_session.add(application)
            current_app.db_session.commit()
            current_app.db_session.refresh(application)

        return applications, 201
