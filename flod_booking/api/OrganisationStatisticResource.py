#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date
from flask import current_app, request
from flask.ext.restful import fields, marshal, abort
from flask.ext.bouncer import requires, GET
from BaseResource import BaseResource, get_organisation_for_uri
from domain.models import Application, Resource, Slot, RepeatingSlot, StrotimeSlot
from sqlalchemy import func, Date, cast


organisation_statistic_fields = {
    'resource_uri': fields.String,
    'hours': fields.Float
}


class OrganisationStatisticResource(BaseResource):
    @requires(GET, 'OrganisationStatistic')
    def get(self, organisation_id):

        if "start_date" in request.args and "end_date" in request.args:
            start_date, end_date = self.parse_date_range_from_args(request)
        else:
            abort(404, __error__=["No date or date interval specified."])

        statuses = ["Granted"]

        organisation = get_organisation_for_uri("/organisations/%s" % organisation_id)

        single_booking = current_app.db_session.query(Resource.uri.label("resource_uri"), func.sum(Slot.end_time - Slot.start_time).label("time")) \
            .filter(Application.organisation_id == organisation.id,
                    Slot.application_id == Application.id,
                    Resource.id == Application.resource_id,
                    Application.status.in_(statuses),
                    # Get all slots between start and end date
                    cast(Slot.start_time, Date).between(start_date, end_date),
                    cast(Slot.end_time, Date).between(start_date, end_date),
                    ) \
            .group_by(Resource.uri)

        strotime_booking = current_app.db_session.query(Resource.uri.label("resource_uri"), func.sum(StrotimeSlot.end_time - StrotimeSlot.start_time).label("time")) \
            .filter(Application.organisation_id == organisation.id,
                    StrotimeSlot.application_id == Application.id,
                    Resource.id == Application.resource_id,
                    Application.status.in_(statuses),
                    # Get all slots between start and end date
                    cast(StrotimeSlot.start_time, Date).between(start_date, end_date),
                    cast(StrotimeSlot.end_time, Date).between(start_date, end_date),
                    ) \
            .group_by(Resource.uri)

        repeating_booking = current_app.db_session.query(Resource.uri.label("resource_uri"), RepeatingSlot.start_date, RepeatingSlot.end_date, RepeatingSlot.start_time,
                                                         RepeatingSlot.end_time, RepeatingSlot.week_day) \
            .filter(Application.organisation_id == organisation.id,
                    RepeatingSlot.application_id == Application.id,
                    Resource.id == Application.resource_id,
                    Application.status.in_(statuses),
                    # Get all slots between start and end date
                    cast(RepeatingSlot.start_date, Date) <= end_date,
                    cast(RepeatingSlot.end_date, Date) >= start_date,
                    )

        results = []
        for single in single_booking.all():
            add_hours(results, single)

        for strotime in strotime_booking.all():
            add_hours(results, strotime)

        for repeating in repeating_booking.all():
            start = repeating.start_date
            if start < start_date:
                start = start_date

            end = repeating.end_date
            if end > end_date:
                end = end_date

            weeks = (end - start).days / 7

            starthours = datetime.combine(date.min, repeating.start_time)
            endhours = datetime.combine(date.min, repeating.end_time)

            hours = (endhours - starthours).total_seconds() / 3600.0

            total_hours = hours * weeks

            if ((end == start and start.isoweekday() == repeating.week_day)  # exact day
                or ((end - start).days % 7 != 0  # remaining week
                    # repeating weekday after start and before end. I.E start is tuesday, repeating is wednesday, end is friday
                    and ((start.isoweekday() <= repeating.week_day <= end.isoweekday())
                         # repeating weekday before start and before end, and start is after end. I.E start is friday, repeating is tuesday and end is wednesday
                         or (end.isoweekday() <= start.isoweekday() >= repeating.week_day <= end.isoweekday())))):
                total_hours += hours

            if total_hours > 0:
                item = find_resource(results, repeating.resource_uri)
                item['hours'] += total_hours

        return marshal(results, organisation_statistic_fields)


def find_resource(list, resource_uri):
    for item in list:
        if item['resource_uri'] == resource_uri:
            return item
    item = {'resource_uri': resource_uri, 'hours': 0.0}
    list.append(item)
    return item


def add_hours(list, booking):
    item = find_resource(list, booking.resource_uri)
    item['hours'] += booking.time.total_seconds() / 3600.0
