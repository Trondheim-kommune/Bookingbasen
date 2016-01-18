# -*- coding: utf-8 -*-

from flask import request, current_app
from flask.ext.restful import fields, marshal, abort
from flask.ext.bouncer import requires, ensure, POST
from isodate import parse_date, parse_datetime

from BaseResource import ISO8601DateTime
from BlockedTimeBaseResource import BlockedTimeBaseResource
from ResourceResource import resource_fields
from domain.models import BlockedTimeInterval
import datetime

blocked_time_interval_fields = {
    'id': fields.Integer,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'note'     : fields.String,
    'resource' : fields.Nested(resource_fields)
}

class BlockedTimeIntervalResource(BlockedTimeBaseResource):
    t = BlockedTimeInterval
    type_name = "blocked time interval"
    fields = blocked_time_interval_fields

    @requires(POST, BlockedTimeInterval)
    def post(self, resource_id = None):
        data = request.get_json()

        # Resource id might also be part of the incoming json.
        resource_uri = None
        if not resource_id:
            resource_uri = data["resource_uri"]

        resource = self.get_resource_with_id_or_uri(resource_id, resource_uri)

        start_time = parse_datetime(data["start_time"])
        end_time = parse_datetime(data["end_time"])
        if data["note"]:
            note = data["note"]
            if not (len(note) <= 50):
                abort(400, __error__=[u'Maks lengde for merknad er 50 tegn'])
        else:
            note= ""

        # Check that the time has correct minute interval, only 30-minute intervals allowed
        invalid_minutes = filter(lambda my_time: my_time.minute not in [0, 30], [start_time, end_time])
        if invalid_minutes:
            abort(400,
                  __error__=[u'Tidene må angis i hele halvtimer']
            )

        blocked_time_interval = BlockedTimeInterval(resource, start_time, end_time, note)
        ensure(POST, blocked_time_interval)

        start_date = start_time.date()
        end_date = end_time.date()
        start_time = start_time.time()
        end_time = end_time.time()

        self.validate_start_and_end_times(start_date, end_date, start_time, end_time)

        # Find out which ISO week days this blocking covers
        week_days = []
        d = start_date
        delta = datetime.timedelta(days=1)
        while d <= end_date:
            week_days.append(d.isoweekday())
            d += delta

        for week_day in week_days:
                #if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time) or \
                #        self.is_conflict_rammetid(resource, start_date, end_date, week_day, start_time, end_time):
                #    abort(
                #        400,
                #        __error__=[u'Tiden er ikke tilgjengelig for blokkering']
                #    )
                if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(
                        400,
                        __error__=[u'Tiden er allerede blokkert']
                    )

        current_app.db_session.add(blocked_time_interval)
        current_app.db_session.commit()
        current_app.db_session.refresh(blocked_time_interval)

        return marshal(blocked_time_interval, self.fields), 201
