# -*- coding: utf-8 -*-
from datetime import date

from flask import current_app, request
from flask.ext.restful import fields, marshal_with, abort
from flask.ext.bouncer import requires, ensure, PUT
from isodate import parse_date, parse_time
from datetime import timedelta
from sqlalchemy.orm.exc import NoResultFound

from BaseResource import ISO8601DateTime
from domain.models import RepeatingSlot
from BaseApplicationResource import BaseApplicationResource

repeating_slot_fields = {
    'id': fields.Integer,
    'start_date': ISO8601DateTime,
    'end_date': ISO8601DateTime,
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,
}


class RepeatingSlotReleaseTimeResource(BaseApplicationResource):
    @requires(PUT, RepeatingSlot)
    @marshal_with(repeating_slot_fields)
    def put(self, slot_id):
        try:
            slot = current_app.db_session.query(RepeatingSlot).filter(RepeatingSlot.id == slot_id).one()
        except NoResultFound:
            abort(404, __error__=[u"No slot found with id %d." % slot_id])

        ensure(PUT, slot)
        args = request.get_json()

        if slot.application.status != 'Granted':
            abort(400, __error__=[u'Kan ikke frigi tid når søknaden ikke er godkjent'])

        if slot.end_date <= date.today():
            abort(400, __error__=[u'Kan ikke frigi allerede brukt tid'])

        repeating_slots = []

        if "release_from_date" in args or "release_to_date" in args:
            release_from_date = parse_date(args["release_from_date"])
            release_to_date = parse_date(args["release_to_date"])

            if release_from_date > release_to_date:
                abort(400, __error__=[u'Startdato er etter sluttdato'])

            if release_from_date <= date.today():
                abort(400, __error__=[u'Kan kun frigi tid frem i tid'])

            if release_from_date <= slot.start_date and release_to_date >= slot.end_date:
                abort(400, __error__=[u'Du kan ikke frigi hele perioden'])

            intervals = [{
                "start": release_from_date - timedelta(days=1),
                "end": release_to_date + timedelta(days=1)
            }]
            periods = self.split_range_by_intervals(slot.start_date, slot.end_date, intervals)
            for period in periods:
                repeating_slots.append(RepeatingSlot(slot.application, slot.week_day,
                                                     period['start'], period['end'],
                                                     slot.start_time, slot.end_time, ))

        if "release_from_time" in args or "release_to_time" in args:
            release_from_time = parse_time(args["release_from_time"])
            release_to_time = parse_time(args["release_to_time"])
            if release_from_time > release_to_time:
                abort(400, __error__=[u'Starttidspunkt er etter slutttidspunkt'])

            if release_from_time <= slot.start_time and release_to_time >= slot.end_time:
                abort(400, __error__=[u'Du kan ikke frigi hele tidsperioden'])

            split_slot = slot
            if slot.start_date <= date.today():
                intervals = [{
                    "start": date.today(),
                    "end": date.today()
                }]
                periods = self.split_range_by_intervals(slot.start_date, slot.end_date, intervals)
                # add period for past
                repeating_slots.append(RepeatingSlot(slot.application, slot.week_day,
                                                     periods[0]['start'], periods[0]['end'],
                                                     slot.start_time, slot.end_time))
                # continue splitting the future
                split_slot = RepeatingSlot(slot.application, slot.week_day,
                                           periods[1]['start'], periods[1]['end'],
                                           slot.start_time, slot.end_time)

            intervals = [{
                "start": release_from_time,
                "end": release_to_time
            }]
            periods = self.split_range_by_intervals(split_slot.start_time, split_slot.end_time, intervals)
            for period in periods:
                repeating_slots.append(RepeatingSlot(split_slot.application, split_slot.week_day,
                                                     split_slot.start_date + timedelta(days=1), split_slot.end_date,
                                                     period['start'], period['end']))

        # Remove old slot if new slots are generated
        if len(repeating_slots) > 0:
            current_app.db_session.delete(slot)

        # Add new slot(s)
        for repeating_slot in repeating_slots:
            current_app.db_session.add(repeating_slot)
        current_app.db_session.commit()

        return repeating_slots, 200
