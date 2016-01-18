#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date
from flask import current_app, request
from flask.ext.restful import fields, marshal, abort
from flask.ext.bouncer import requires, GET
from BaseResource import BaseResource, get_resource_for_uri, get_resource_from_web
from domain.models import Application, Organisation, Slot, RepeatingSlot, StrotimeSlot
from sqlalchemy import func, Date, cast

resource_statistic_fields = {
    'organisation_uri': fields.String,
    'hours': fields.Float,
    'area_time': fields.Float
}


def get_resource_statistic(facility_id, start_date, end_date):
    resource_uri = "/facilities/%s" % facility_id
    resource = get_resource_for_uri(resource_uri)
    resource_details = get_resource_from_web(resource_uri)
    resource_area = resource_details['area']

    statuses = ["Granted"]

    resource_id = resource.id
    single_booking = current_app.db_session.query(Organisation.uri.label("organisation_uri"), func.sum(Slot.end_time - Slot.start_time).label("time")) \
        .outerjoin(Application.organisation) \
        .filter(Application.resource_id == resource_id,
                Slot.application_id == Application.id,
                Application.to_be_invoiced != True,  # != True to include both False and None
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(Slot.start_time, Date).between(start_date, end_date),
                cast(Slot.end_time, Date).between(start_date, end_date),
                ) \
        .group_by(Organisation.uri)

    strotime_booking = current_app.db_session.query(Organisation.uri.label("organisation_uri"), func.sum(StrotimeSlot.end_time - StrotimeSlot.start_time).label("time")) \
        .outerjoin(Application.organisation) \
        .filter(Application.resource_id == resource_id,
                StrotimeSlot.application_id == Application.id,
                Application.to_be_invoiced != True,  # != True to include both False and None
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(StrotimeSlot.start_time, Date).between(start_date, end_date),
                cast(StrotimeSlot.end_time, Date).between(start_date, end_date),
                ) \
        .group_by(Organisation.uri)

    repeating_booking = current_app.db_session.query(Organisation.uri.label("organisation_uri"), RepeatingSlot.start_date, RepeatingSlot.end_date, RepeatingSlot.start_time,
                                                     RepeatingSlot.end_time, RepeatingSlot.week_day) \
        .outerjoin(Application.organisation) \
        .filter(Application.resource_id == resource_id,
                RepeatingSlot.application_id == Application.id,
                Application.to_be_invoiced != True,  # != True to include both False and None
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(RepeatingSlot.start_date, Date) <= end_date,
                cast(RepeatingSlot.end_date, Date) >= start_date,
                )

    results = []
    for single in single_booking.all():
        add_hours(results, single, resource_area)

    for strotime in strotime_booking.all():
        add_hours(results, strotime, resource_area)

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
            item = find_organisation(results, repeating.organisation_uri)
            item['hours'] += total_hours
            item['area_time'] += total_hours * resource_area

    return marshal(results, resource_statistic_fields)


class ResourceStatisticResource(BaseResource):
    @requires(GET, 'ResourceStatistic')
    def get(self, facility_id):

        if "start_date" in request.args and "end_date" in request.args:
            start_date, end_date = self.parse_date_range_from_args(request)
        else:
            abort(404, __error__=["No date or date interval specified."])

        return get_resource_statistic(facility_id, start_date, end_date)


def find_organisation(list, organisation_uri):
    for item in list:
        if item['organisation_uri'] == organisation_uri:
            return item
    item = {'organisation_uri': organisation_uri, 'hours': 0.0, 'area_time': 0.0}
    list.append(item)
    return item


def add_hours(list, booking, resource_area):
    item = find_organisation(list, booking.organisation_uri)
    item['hours'] += booking.time.total_seconds() / 3600.0
    item['area_time'] += (booking.time.total_seconds() / 3600) * resource_area
