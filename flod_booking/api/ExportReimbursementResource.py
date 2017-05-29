# -*- coding: utf-8 -*-
from collections import OrderedDict

from datetime import datetime, date, time
from isodate import parse_date
from flask import current_app
from flask.ext.bouncer import requires, GET
from api.BaseResource import BaseResource, get_resource_for_uri, get_resource_from_web
from domain.models import Application, Slot, RepeatingSlot, StrotimeSlot, WeeklyBlockedTime, BlockedTimeInterval
from sqlalchemy import func, Date, cast, Integer
from flod_common.outputs.output_csv import output_csv


def get_resource_statistic(facility_id, start_date, end_date):
    resource_uri = "/facilities/%s" % facility_id
    resource = get_resource_for_uri(resource_uri)
    resource_id = resource.id
    statuses = ["Granted"]

    sum_hours = 0.0
    sum_invoiced_hours = 0.0

    hours, invoiced_hours = get_slot_hours(resource_id, statuses, start_date, end_date)
    sum_hours += hours
    sum_invoiced_hours += invoiced_hours

    hours, invoiced_hours = get_strotime_slot_hours(resource_id, statuses, start_date, end_date)
    sum_hours += hours
    sum_invoiced_hours += invoiced_hours

    hours, invoiced_hours = get_repeating_slot_hours(resource_id, statuses, start_date, end_date)
    sum_hours += hours
    sum_invoiced_hours += invoiced_hours

    sum_blocked_hours = 0.0
    sum_blocked_hours += get_blocked_interval_hours(resource_id, start_date, end_date)
    sum_blocked_hours += get_weekly_blocked_hours(resource_id, start_date, end_date)

    results = {"hours": sum_hours, "invoiced_hours": sum_invoiced_hours, "blocked_hours": sum_blocked_hours}
    return results


def get_weekly_blocked_hours(resource_id, start_date, end_date):
    sum_blocked_hours = 0.0
    weekly_blocked = current_app.db_session.query(WeeklyBlockedTime.start_date, WeeklyBlockedTime.end_date, WeeklyBlockedTime.start_time,
                                                  WeeklyBlockedTime.end_time, WeeklyBlockedTime.week_day) \
        .filter(WeeklyBlockedTime.resource_id == resource_id,
                # Get all weekly blocked time between start and end date
                cast(WeeklyBlockedTime.start_date, Date) <= end_date,
                cast(WeeklyBlockedTime.end_date, Date) >= start_date,
                )
    for weekly in weekly_blocked.all():
        start = weekly.start_date
        if start < start_date:
            start = start_date

        end = weekly.end_date
        if end > end_date:
            end = end_date

        weeks = (end - start).days / 7

        starthours = datetime.combine(date.min, weekly.start_time)
        endhours = datetime.combine(date.min, weekly.end_time)

        hours = (endhours - starthours).total_seconds() / 3600.0
        total_hours = hours * weeks
        if ((end == start and start.isoweekday() == weekly.week_day)  # exact day
            or ((end - start).days % 7 != 0  # remaining week
                # repeating weekday after start and before end. I.E start is tuesday, repeating is wednesday, end is friday
                and ((start.isoweekday() <= weekly.week_day <= end.isoweekday())
                     # repeating weekday before start and before end, and start is after end. I.E start is friday, repeating is tuesday and end is wednesday
                     or (end.isoweekday() <= start.isoweekday() >= weekly.week_day <= end.isoweekday())))):
            total_hours += hours

        if total_hours > 0:
            sum_blocked_hours += total_hours
    return sum_blocked_hours


def get_blocked_interval_hours(resource_id, start_date, end_date):
    sum_blocked_hours = 0.0
    interval_blocked = current_app.db_session.query(BlockedTimeInterval.start_time, BlockedTimeInterval.end_time) \
        .filter(BlockedTimeInterval.resource_id == resource_id,
                # Get all blocked time intervals between start and end date
                cast(BlockedTimeInterval.start_time, Date) <= end_date,
                cast(BlockedTimeInterval.end_time, Date) >= start_date,
                )
    for interval in interval_blocked.all():
        interval_start = interval.start_time
        if interval_start.date() < start_date:
            interval_start = datetime.combine(start_date, time(8, 0))
        interval_end = interval.end_time
        if interval_end.date() > end_date:
            interval_end = datetime.combine(end_date, time(23, 0))

        blocked_interval_hours = (((interval_end.date() - interval_start.date()).days + 1) * (23 - 8)  # total number of hours in whole period
                                  - (interval_start - datetime.combine(interval_start.date(),
                                                                       time(8))).total_seconds() / 3600.0  # minus adjustment for late start
                                  - (datetime.combine(interval_end.date(), time(23)) - interval_end).total_seconds() / 3600.0)  # minus adjustment for early end
        sum_blocked_hours += blocked_interval_hours

    return sum_blocked_hours


def get_repeating_slot_hours(resource_id, statuses, start_date, end_date):
    sum_hours = 0.0
    sum_invoiced_hours = 0.0

    repeating_booking = current_app.db_session.query(RepeatingSlot.start_date, RepeatingSlot.end_date, RepeatingSlot.start_time,
                                                     RepeatingSlot.end_time, RepeatingSlot.week_day, Application.to_be_invoiced) \
        .filter(Application.resource_id == resource_id,
                RepeatingSlot.application_id == Application.id,
                # Application.to_be_invoiced != True,  # != True to include both False and None
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(RepeatingSlot.start_date, Date) <= end_date,
                cast(RepeatingSlot.end_date, Date) >= start_date,
                )
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
            if repeating.to_be_invoiced:
                sum_invoiced_hours += total_hours
            else:
                sum_hours += total_hours
    return sum_hours, sum_invoiced_hours


def get_strotime_slot_hours(resource_id, statuses, start_date, end_date):
    sum_hours = 0.0
    sum_invoiced_hours = 0.0

    # get strøtimer
    strotime_booking = current_app.db_session.query(
        func.sum((StrotimeSlot.end_time - StrotimeSlot.start_time) * cast(Application.to_be_invoiced != True, Integer)).label("time"),
        # != True to include both False and None
        func.sum((StrotimeSlot.end_time - StrotimeSlot.start_time) * cast(Application.to_be_invoiced == True, Integer)).label("invoiced_time")) \
        .filter(Application.resource_id == resource_id,
                StrotimeSlot.application_id == Application.id,
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(StrotimeSlot.start_time, Date).between(start_date, end_date),
                cast(StrotimeSlot.end_time, Date).between(start_date, end_date),
                )
    strotime = strotime_booking.first()
    if strotime.time:
        sum_hours = strotime.time.total_seconds() / 3600.0
    if strotime.invoiced_time:
        sum_invoiced_hours += strotime.invoiced_time.total_seconds() / 3600.0

    return sum_hours, sum_invoiced_hours


def get_slot_hours(resource_id, statuses, start_date, end_date):
    sum_hours = 0.0
    sum_invoiced_hours = 0.0

    single_booking = current_app.db_session.query(func.sum((Slot.end_time - Slot.start_time) * cast(Application.to_be_invoiced != True, Integer)).label("time"),  # != True to include both False and None
                                                  func.sum((Slot.end_time - Slot.start_time) * cast(Application.to_be_invoiced == True, Integer)).label("invoiced_time")) \
        .filter(Application.resource_id == resource_id,
                Slot.application_id == Application.id,
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(Slot.start_time, Date).between(start_date, end_date),
                cast(Slot.end_time, Date).between(start_date, end_date),
                )
    single = single_booking.first()
    if single.time:
        sum_hours = single.time.total_seconds() / 3600.0
    if single.invoiced_time:
        sum_invoiced_hours = single.invoiced_time.total_seconds() / 3600.0

    return sum_hours, sum_invoiced_hours


def get_statistics(start_date, end_date):
    result = []

    resource_data = get_resource_from_web('/facilities/')

    for facility in resource_data:
        facility_id = facility.get('id')
        facility_statistics_response = get_resource_statistic(facility_id, start_date, end_date)

        result.append({
            # 'id': facility_id,
            'unit_type': facility.get('unit_type').get('name'),
            'unit_number': facility.get('unit_number'),
            'unit_name': facility.get('unit_name'),
            'name': facility.get('name'),
            # 'facility_type': facility.get('facility_type').get('name'),
            'hours': float(facility_statistics_response['hours']),
            'invoiced_hours': float(facility_statistics_response['invoiced_hours']),
            'blocked_hours': float(facility_statistics_response['blocked_hours'])})

    return result


class ExportReimbursementResource(BaseResource):
    @requires(GET, 'ExportReimbursement')
    def get(self, start, end):
        start_date = parse_date(start)
        end_date = parse_date(end)

        statistics = get_statistics(start_date, end_date)

        fieldname_mapping = OrderedDict()
        fieldname_mapping['unit_type'] = 'Type enhet'
        fieldname_mapping['unit_number'] = 'Enhetskode'
        fieldname_mapping['unit_name'] = 'Navn på enhet'
        fieldname_mapping['name'] = 'Navn på lokalet'
        fieldname_mapping['hours'] = 'Antall timer utlån fra %s til %s' % (start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
        fieldname_mapping['invoiced_hours'] = 'Antall fakturerte timer utleie fra %s til %s' % (start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
        fieldname_mapping['blocked_hours'] = 'Antall blokkerte timer fra %s til %s' % (start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))

        return output_csv(statistics, 200, fieldname_mapping=fieldname_mapping)
