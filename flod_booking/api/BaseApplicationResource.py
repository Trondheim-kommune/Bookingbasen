# -*- coding: utf-8 -*-

from flask import current_app
from sqlalchemy import and_, or_, Date, Time, cast, extract, tuple_, DateTime, func, text

from flask.ext.restful import abort

from BaseResource import BaseResource
from domain.models import Application, Slot, RepeatingSlot, StrotimeSlot, \
    WeeklyBlockedTime, BlockedTimeInterval, RammetidSlot, Rammetid
from datetime import timedelta, datetime, time
from api_exceptions import format_exception


def nearest_hour(date):
    plus_one = date + timedelta(hours=1)
    year = plus_one.year
    month = plus_one.month
    day = plus_one.day
    hour = plus_one.hour
    return datetime(year=year, month=month, day=day, hour=hour)


class BaseApplicationResource(BaseResource):
    method_decorators = [format_exception]

    @classmethod
    def is_conflict_rammetid(cls, resource, start_date, end_date, week_day, start_time, end_time):
        rammetid_slots = cls.get_rammetid_slots(resource, start_date, end_date, week_day, start_time, end_time)
        if len(rammetid_slots) > 0:
            return True
        return False

    @classmethod
    def is_conflict_slot_time(cls, resource, start_date, end_date, week_day, start_time, end_time):
        repeating_slots = cls.get_repeating_slots(resource, start_date, end_date, week_day, start_time, end_time)
        if len(repeating_slots) > 0:
            return True
        strotime_slots = cls.get_strotime_slots(resource, start_date, end_date, week_day, start_time, end_time)
        if len(strotime_slots) > 0:
            return True
        slots = cls.get_slots(resource, start_date, end_date, week_day, start_time, end_time)
        if len(slots) > 0:
            return True
        return False

    @classmethod
    def is_conflict_blocked_time(cls, resource, start_date, end_date, week_day, start_time, end_time):
        blocked_time_intervals = cls.get_blocked_time_intervals(resource, start_date, end_date, week_day, start_time, end_time)
        if len(blocked_time_intervals) > 0:
            return True
        weekly_blocked_times = cls.get_weekly_blocked_times(resource, start_date, end_date, week_day, start_time, end_time)
        if len(weekly_blocked_times) > 0:
            return True
        return False

    @classmethod
    def get_repeating_slots(cls, resource, start_date, end_date, week_day, start_time, end_time):
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
            ),
            tuple_(
                RepeatingSlot.start_time, RepeatingSlot.end_time
            ).op('overlaps')(
                tuple_(
                    cast(start_time, Time), cast(end_time, Time)
                )
            ),
            and_(
                week_day == RepeatingSlot.week_day
            )
        )
        return objects.all()

    @classmethod
    def get_rammetid_slots(cls, resource, start_date, end_date, week_day, start_time, end_time):
        query = current_app.db_session.query(RammetidSlot)
        objects = query.filter(Rammetid.resource == resource,
                               RammetidSlot.rammetid_id == Rammetid.id)
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
            tuple_(
                RammetidSlot.start_time, RammetidSlot.end_time
            ).op('overlaps')(
                tuple_(
                    cast(start_time, Time), cast(end_time, Time)
                )
            ),
            and_(
                week_day == RammetidSlot.week_day
            )
        )
        return objects.all()

    @classmethod
    def get_strotime_slots(cls, resource, start_date, end_date, week_day, start_time, end_time):
        query = current_app.db_session.query(StrotimeSlot)
        statuses = ["Granted"]
        objects = query.filter(Application.resource == resource,
                               StrotimeSlot.application_id == Application.id,
                               Application.status.in_(statuses))
        objects = objects.filter(
            or_(
                tuple_(
                    cast(StrotimeSlot.start_time, Date), cast(StrotimeSlot.end_time, Date)
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    cast(StrotimeSlot.end_time, Date) == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == cast(StrotimeSlot.start_time, Date)
                )
            ),
            tuple_(
                cast(StrotimeSlot.start_time, Time), cast(StrotimeSlot.end_time, Time)
            ).op('overlaps')(
                tuple_(
                    cast(start_time, Time), cast(end_time, Time)
                )
            ),
            and_(
                extract('ISODOW', StrotimeSlot.start_time) == week_day
            )
        )
        return objects.all()

    @classmethod
    def get_slots(cls, resource, start_date, end_date, week_day, start_time, end_time):
        query = current_app.db_session.query(Slot)
        statuses = ["Granted"]
        objects = query.filter(Application.resource == resource,
                               Slot.application_id == Application.id,
                               Application.status.in_(statuses))

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
            ),
            tuple_(
                cast(Slot.start_time, Time), cast(Slot.end_time, Time)
            ).op('overlaps')(
                tuple_(
                    cast(start_time, Time), cast(end_time, Time)
                )
            ),
            and_(
                extract('ISODOW', Slot.start_time) == week_day
            )
        )
        return objects.all()

    @classmethod
    def get_blocked_time_intervals(cls, resource, start_date, end_date, week_day, start_time, end_time):
        def get_next_weekday(start_date, week_day):
            days_ahead = week_day - start_date.isoweekday()
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        def get_previous_weekday(end_date, week_day):
            days_behind = week_day - end_date.isoweekday()
            if days_behind > 0:  # Target day already happened this week
                days_behind -= 7
            return end_date + timedelta(days=days_behind)

        # adjust start and end date to match week day
        start_date = get_next_weekday(start_date, week_day)
        end_date = get_previous_weekday(end_date, week_day)

        # if start_date is after end_date, there is no period to check against anymore
        if start_date > end_date:
            return []

        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        query = current_app.db_session.query(BlockedTimeInterval)
        objects = query.filter(BlockedTimeInterval.resource == resource)

        objects = objects.filter(
            or_(
                tuple_(
                    BlockedTimeInterval.start_time, BlockedTimeInterval.end_time
                ).op('overlaps')(
                    tuple_(
                        cast(start_datetime, DateTime), cast(end_datetime, DateTime)
                    )
                )
            ),
            or_(
                (func.LEAST(cast(end_datetime, Date), cast(BlockedTimeInterval.end_time, Date)) - func.GREATEST(cast(start_datetime, Date),
                                                                                                                cast(BlockedTimeInterval.start_time, Date))) >= 6,
                text(
                    "EXISTS (SELECT 1 FROM (SELECT EXTRACT(ISODOW FROM generate_series(GREATEST(:start_date, blocked_time_intervals.start_time), LEAST(:end_date, blocked_time_intervals.end_time), CAST('1 day' as INTERVAL))) AS weekday) as weekdays WHERE weekdays.weekday = :week_day)"
                ).params(start_date=start_datetime, end_date=end_datetime, week_day=week_day)
            )
        )

        return objects.all()

    @classmethod
    def get_weekly_blocked_times(cls, resource, start_date, end_date, week_day, start_time, end_time):
        query = current_app.db_session.query(WeeklyBlockedTime)
        objects = query.filter(WeeklyBlockedTime.resource == resource)
        objects = objects.filter(
            or_(
                tuple_(
                    WeeklyBlockedTime.start_date, WeeklyBlockedTime.end_date
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    WeeklyBlockedTime.end_date == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == WeeklyBlockedTime.start_date
                )
            ),
            tuple_(
                WeeklyBlockedTime.start_time, WeeklyBlockedTime.end_time
            ).op('overlaps')(
                tuple_(
                    cast(start_time, Time), cast(end_time, Time)
                )
            ),
            and_(
                week_day == WeeklyBlockedTime.week_day
            )
        )
        return objects.all()

    @classmethod
    def validate_start_and_end_times(cls, start_date, end_date, start_time, end_time):
        """
        General validation that is applied to _all_ types of applications.

        :exception: Exception if validation rules are violated
        """

        # 1. verify that start_date is before or same as end_date
        if start_date > end_date:
            abort(400,
                  __error__=[u'Starttidspunkt kan ikke være etter sluttidspunkt']
                  )

        # 2. verify that start_time is before end_time; if on the same day
        if start_date == end_date:
            if start_time >= end_time:
                abort(400,
                      __error__=[u'Starttidspunkt må være før sluttidspunkt']
                      )

        # 3. verify that start_time is no earlier than 0800 and end_time is no later than 2300
        min_time = time(hour=8, minute=0, second=0)
        if start_time < min_time or end_time < min_time:
            abort(400,
                  __error__=[u'Start -og/eller sluttidspunkt kan ikke være før klokka 0800']
                  )
        max_time = time(hour=23, minute=0, second=0)
        if start_time > max_time or end_time > max_time:
            abort(400,
                  __error__=[u'Start -og/eller sluttidspunkt kan ikke være etter klokka 2300']
                  )


    @classmethod
    def validate_end_date_of_slot(cls, booking_enddate, slot_enddate, app_type):
        if booking_enddate and slot_enddate > booking_enddate:
            abort(400,
                  __error__=[
                      u'Det er ikke mulig å søke om %s i denne perioden. <a href="http://www.trondheim.kommune.no/lokaler/type" target="_blank">Mer informasjon</a>' % app_type])
