# -*- coding: utf-8 -*-
from flask import request, current_app
from datetime import datetime
from flask.ext.restful import marshal_with, fields, abort
from sqlalchemy import or_, Date, cast, tuple_, func, text

from api_exceptions import format_exception
from BaseResource import BaseResource, ISO8601DateTime
from domain.models import RammetidSlot, Rammetid, UmbrellaOrganisation, RepeatingSlot, Application, Slot
from common_fields import umbrella_organisation_fields

week_rammetid_slot_fields = {
    'id': fields.Integer(default=None),
    'start_date': ISO8601DateTime,
    'end_date': ISO8601DateTime,
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,
    'rammetid_id': fields.Integer,
    'umbrella_organisation': fields.Nested(umbrella_organisation_fields)
}


class WeeklyRammetidSlotsResource(BaseResource):
    method_decorators = [format_exception]

    def get_rammetid_slots(self, resource, except_rammetids, start_date, end_date, umbrella_organisation_uri):
        query = current_app.db_session.query(RammetidSlot)
        objects = query.filter(Rammetid.resource == resource,
                               RammetidSlot.rammetid_id == Rammetid.id,
                               Rammetid.umbrella_organisation_id == UmbrellaOrganisation.id)

        if except_rammetids:
            objects = objects.filter(
                ~RammetidSlot.rammetid_id.in_(except_rammetids)
            )

        if umbrella_organisation_uri:
            objects = objects.filter(
                UmbrellaOrganisation.uri == umbrella_organisation_uri
            )
        objects = objects.filter(
            or_(
                tuple_(
                    RammetidSlot.start_date, RammetidSlot.end_date
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    RammetidSlot.end_date == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == RammetidSlot.start_date
                )
            ),
            or_(
                (func.LEAST(cast(end_date, Date), RammetidSlot.end_date) - func.GREATEST(cast(start_date, Date), RammetidSlot.start_date)) >= 6,
                RammetidSlot.week_day.in_(
                    text(
                        "SELECT EXTRACT(ISODOW FROM generate_series(GREATEST(:start_date, rammetid_slots.start_date), LEAST(:end_date, rammetid_slots.end_date), CAST('1 day' as INTERVAL)))"
                    ).params(start_date=start_date, end_date=end_date))
            )
        )
        return objects.all()

    def get_repeating_slots(self, resource, start_date, end_date):
        query = current_app.db_session.query(RepeatingSlot)
        statuses = ["Granted"]
        objects = query.filter(Application.resource == resource,
                               RepeatingSlot.application_id == Application.id,
                               Application.status.in_(statuses))

        objects = objects.filter(
            or_(
                tuple_(
                    RepeatingSlot.start_date, RepeatingSlot.end_date
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    RepeatingSlot.end_date == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == RepeatingSlot.start_date
                )
            )
        )
        return objects.order_by(RepeatingSlot.start_time).all()

    def get_arrangements_slots(self, resource, start_date, end_date):  # start_time, end_time, week_day
        query = current_app.db_session.query(Slot)
        statuses = ["Granted"]
        objects = query.filter(Application.resource == resource,
                               Slot.application_id == Application.id,
                               Application.status.in_(statuses),
                               Application.is_arrangement == True)

        objects = objects.filter(
            or_(
                tuple_(
                    cast(Slot.start_time, Date), cast(Slot.end_time, Date)
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    cast(Slot.end_time, Date) == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == cast(Slot.start_time, Date)
                )
            )
        )
        return objects.order_by(Slot.start_time).all()

    @marshal_with(week_rammetid_slot_fields)
    def get(self):
        resource_uri = request.args.get('resource_uri')
        except_rammetid = request.args.get('except')
        umbrella_organisation_uri = request.args.get('umbrella_organisation_uri')

        if not "start_date" in request.args or not "end_date" in request.args:
            abort(404, __error__=["start and end date must be set."])

        start_date = datetime.strptime(request.args["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.args["end_date"], "%Y-%m-%d").date()

        resource = self.get_resource_with_id_or_uri(None, resource_uri)

        except_rammetids = []
        if except_rammetid:
            except_rammetids.append(int(except_rammetid))

        results = []
        rammetid_slots = self.get_rammetid_slots(resource, except_rammetids, start_date, end_date, umbrella_organisation_uri)
        if "split_by_slots" in request.args or "split_by_arrangement_slots" in request.args:
            time_intervals = [[] for i in range(1, 9)]
            if "split_by_slots" in request.args:
                slots = self.get_repeating_slots(resource, start_date, end_date)
                for slot in slots:
                    first_occurrence = self.get_first_occurrence(slot.week_day, slot.start_date)
                    last_occurrence = self.get_last_occurrence(slot.week_day, slot.start_date, slot.end_date)
                    time_intervals[first_occurrence.isoweekday()].append({
                        "start": slot.start_time,
                        "end": slot.end_time,
                        "start_week_number": start_date.isocalendar()[1] if first_occurrence < start_date < last_occurrence else first_occurrence.isocalendar()[1]
                    })
            if "split_by_arrangement_slots" in request.args:
                arrangements_slots = self.get_arrangements_slots(resource, start_date, end_date)
                for arrangements_slot in arrangements_slots:
                    week_day = arrangements_slot.start_time.isoweekday()
                    start_time = arrangements_slot.start_time.time()
                    end_time = arrangements_slot.end_time.time()
                    time_intervals[week_day].append({
                        "start": start_time,
                        "end": end_time,
                        "start_week_number": arrangements_slot.start_time.isocalendar()[1],
                        "end_week_number": arrangements_slot.end_time.isocalendar()[1]
                    })
            for time_interval in time_intervals:
                time_interval.sort(key=lambda item: (item['start'], item['end']))

            for rammetid_slot in rammetid_slots:
                time_interval_by_week_number = [item for item in time_intervals[rammetid_slot.week_day] if
                                                max(start_date, rammetid_slot.start_date).isocalendar()[1] == item['start_week_number']]

                periods = self.split_range_by_intervals(rammetid_slot.start_time, rammetid_slot.end_time, time_interval_by_week_number)
                for period in periods:
                    results.append({
                        'start_time': period['start'],
                        'end_time': period['end'],
                        'start_date': rammetid_slot.start_date,
                        'end_date': rammetid_slot.end_date,
                        'week_day': rammetid_slot.week_day,
                        # Setting id to None, because the slot might have been splitted,
                        # otherwise one of the slots with equal id will be eliminated in frontend by backbone.
                        # For the moment rammetid_slot_id is not used anyway, only the reference to rammetid_id
                        'id': None,
                        'rammetid_id': rammetid_slot.rammetid_id,
                        'status': rammetid_slot.rammetid.status,
                        'umbrella_organisation': rammetid_slot.rammetid.umbrella_organisation
                    })
        else:
            for rammetid_slot in rammetid_slots:
                except_rammetids.append(rammetid_slot.rammetid.id)
                results.append({
                    'start_time': rammetid_slot.start_time,
                    'end_time': rammetid_slot.end_time,
                    'start_date': rammetid_slot.start_date,
                    'end_date': rammetid_slot.end_date,
                    'week_day': rammetid_slot.week_day,
                    'id': rammetid_slot.id,
                    'rammetid_id': rammetid_slot.rammetid_id,
                    'status': rammetid_slot.rammetid.status,
                    'umbrella_organisation': rammetid_slot.rammetid.umbrella_organisation
                })

        return results, 200
