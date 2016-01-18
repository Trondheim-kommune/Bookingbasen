# -*- coding: utf-8 -*-

from flask.ext.restful import fields, marshal_with, marshal, abort
from flask.ext.bouncer import requires, ensure, POST
from flask import request, current_app
from isodate import parse_time

from BaseResource import verify_request_contains_mandatory_fields, ISO8601DateTime
from BlockedTimeBaseResource import BlockedTimeBaseResource
from domain.models import WeeklyBlockedTime
from ResourceResource import resource_fields

weekly_blocked_time_fields = {
    'id': fields.Integer,
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
    'note'     : fields.String,
    'resource' : fields.Nested(resource_fields)
}

simple_weekly_blocked_time_fields = {
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
    'note'     : fields.String
}

class WeeklyBlockedTimeResource(BlockedTimeBaseResource):
    t = WeeklyBlockedTime
    type_name = "weekly blocked time"
    fields = weekly_blocked_time_fields
    mandatory_fields = ["start_date", "end_date", "start_time", "end_time", "week_day"]

    def get(self, resource_id=None, uri_name=None, uri_id=None, id=None):
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        if not start_date and not end_date:
            return super(WeeklyBlockedTimeResource, self).get(
                resource_id=resource_id, uri_name=uri_name, uri_id=uri_id, id=id
            )

        if uri_name and uri_id:
            resource_uri = "/%s/%s"%(uri_name, uri_id)
        else:
            resource_uri = request.args.get('resource_uri', None)
        objects = self.get_objects(resource_uri=resource_uri, request=request, union=True)

        return marshal(objects.all(), simple_weekly_blocked_time_fields)

    @requires(POST, WeeklyBlockedTime)
    def post(self, resource_id = None):
        data = request.get_json()
        verify_request_contains_mandatory_fields(data, self.mandatory_fields)

        # Resource id might also be part of the incoming json.
        resource_uri = None
        if not resource_id:
            resource_uri = data["resource_uri"]

        resource = self.get_resource_with_id_or_uri(resource_id, resource_uri)

        start_date, end_date = self.parse_date_range_from_dict(data)

        start_time = parse_time(data["start_time"])
        end_time = parse_time(data["end_time"])
        week_day = data["week_day"]
        if data["note"]:
            note = data["note"]
            if not (len(note) <= 50):
                abort(400, __error__=[u'Maks lengde for merknad er 50 tegn'])
        else:
            note= ""


        self.validate_start_and_end_times(start_date, end_date, start_time, end_time)

        # Check that the time has correct minute interval, only 30-minute intervals allowed
        invalid_minutes = filter(lambda my_time: my_time.minute not in [0, 30], [start_time, end_time])
        if invalid_minutes:
            abort(400,
                  __error__=[u'Tidene må angis i hele halvtimer']
            )

        weekly_blocked_time = WeeklyBlockedTime(resource, week_day,
            start_date, end_date, start_time, end_time, note)
        ensure(POST, weekly_blocked_time)

        if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time) or \
                self.is_conflict_rammetid(resource, start_date, end_date, week_day, start_time, end_time):
            abort(
                400,
                __error__=[u'Tiden er ikke tilgjengelig for blokkering']
            )       
        if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
            abort(
                400,
                __error__=[u'Tiden er allerede blokkert']
            )                 

        current_app.db_session.add(weekly_blocked_time)
        current_app.db_session.commit()
        current_app.db_session.refresh(weekly_blocked_time)

        return marshal(weekly_blocked_time, self.fields), 201
