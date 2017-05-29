# -*- coding: utf-8 -*-
from datetime import date, timedelta
from domain.models import RepeatingSlot
from flask import current_app, request
from flask.ext.bouncer import requires, ensure, PUT
from flask.ext.restful import marshal_with, abort
from isodate import parse_date, parse_time
from sqlalchemy.orm.exc import NoResultFound

from BaseApplicationResource import BaseApplicationResource
from RepeatingSlotResource import repeating_slot_fields


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
        # validate
        if not ("release_from_date" in args and "release_to_date" in args):
            abort(400, __error__=[u'Datointervall må oppgis'])
        if not ("release_from_time" in args and "release_to_time" in args):
            abort(400, __error__=[u'Tidsintervall må oppgis'])
        release_from_date = parse_date(args["release_from_date"])
        release_to_date = parse_date(args["release_to_date"])
        release_from_time = parse_time(args["release_from_time"])
        release_to_time = parse_time(args["release_to_time"])

        if slot.application.status != 'Granted':
            abort(400, __error__=[u'Kan ikke frigi tid når søknaden ikke er godkjent'])

        if slot.end_date <= date.today():
            abort(400, __error__=[u'Kan ikke frigi allerede brukt tid'])

        if release_from_date <= date.today():
            abort(400, __error__=[u'Kan kun frigi tid frem i tid'])

        if (release_from_date <= slot.start_date and release_to_date >= slot.end_date
            and release_from_time <= slot.start_time and release_to_time >= slot.end_time):
            abort(400, __error__=[u'Du kan ikke frigi hele perioden og tidsperioden'])

        if release_from_date < slot.start_date or release_from_date > slot.end_date or release_to_date < slot.start_date or release_to_date > slot.end_date:
            abort(400, __error__=[u'Datointervall må være delmengde av tildelt tid'])

        if release_from_time < slot.start_time or release_from_time > slot.end_time or release_to_time < slot.start_time or release_to_time > slot.end_time:
            abort(400, __error__=[u'Tidsintervall må være delmengde av tildelt tid'])

        if release_from_date > release_to_date:
            abort(400, __error__=[u'Startdato er etter sluttdato'])

        if release_from_time > release_to_time:
            abort(400, __error__=[u'Starttidspunkt er etter slutttidspunkt'])

        repeating_slots = []

        # splitting dates
        if release_from_date > slot.start_date or release_to_date < slot.end_date:
            intervals = [{
                "start": release_from_date - timedelta(days=1),
                "end": release_to_date + timedelta(days=1)
            }]
            periods = self.split_range_by_intervals(slot.start_date, slot.end_date, intervals)
            for period in periods:
                repeating_slots.append(RepeatingSlot(slot.application, slot.week_day,
                                                     period['start'], period['end'],
                                                     slot.start_time, slot.end_time, ))
        # continue splitting time
        if release_from_time > slot.start_time or release_to_time < slot.end_time:
            intervals = [{
                "start": release_from_time,
                "end": release_to_time
            }]
            periods = self.split_range_by_intervals(slot.start_time, slot.end_time, intervals)
            for period in periods:
                repeating_slots.append(RepeatingSlot(slot.application, slot.week_day,
                                                     release_from_date, release_to_date,
                                                     period['start'], period['end']))

        # Remove old slot if new slots are generated
        if len(repeating_slots) > 0:
            current_app.db_session.delete(slot)

        # Add new slot(s)
        for repeating_slot in repeating_slots:
            current_app.db_session.add(repeating_slot)
        current_app.db_session.commit()

        return repeating_slots, 200
