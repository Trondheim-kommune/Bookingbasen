# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time

from sqlalchemy import and_
from sqlalchemy.sql import func

from domain.models import WeeklyBlockedTime, BlockedTimeInterval


class BlockedTimeUtil(object):
    @staticmethod
    def _convert_to_range(target_date, start_time, end_time, note):
        start_time = datetime.combine(target_date, start_time)
        end_time = datetime.combine(target_date, end_time)
        return {"start_time": start_time, "end_time": end_time, "note": note}

    @staticmethod
    def _convert_to_interval_to_range(target_date, interval):
        if target_date == interval.start_time.date():
            start_time = interval.start_time
        else:
            start_time = datetime.combine(target_date, time(0, 0, 0))

        if target_date == interval.end_time.date():
            end_time = interval.end_time
        else:
            tomorrow = target_date + timedelta(days=1)
            end_time = datetime.combine(tomorrow, time(0, 0, 0))

        return {"start_time": start_time, "end_time": end_time, "note": interval.note}

    @staticmethod
    def get_blocked_time_for_date(db_session, resource, target_date):
        def filter_by_date(cls, objects, target_date):
            return objects.filter(and_(cls.start_date <= target_date, cls.end_date >= target_date))

        def filter_by_week_day(cls, objects, week_day):
            return objects.filter(cls.week_day == week_day)

        def filter_intervals_by_date(cls, objects, target_date):
            return objects.filter(and_(func.DATE(cls.start_time) <= target_date,
                                       func.DATE(cls.end_time) >= target_date))

        # Get the weekly blocked times which applies to this date and week day
        objects = db_session.query(WeeklyBlockedTime).filter(WeeklyBlockedTime.resource == resource)
        objects = filter_by_date(WeeklyBlockedTime, objects, target_date)
        objects = filter_by_week_day(WeeklyBlockedTime, objects, target_date.isoweekday())

        # Convert the blocked times into a simpler start-end format
        result = []
        for blocked_time in objects.all():
            result.append(BlockedTimeUtil._convert_to_range(target_date,
                                                            blocked_time.start_time,
                                                            blocked_time.end_time,
                                                            blocked_time.note))

        # Get time intervals which applies to this date
        time_intervals = db_session.query(BlockedTimeInterval).filter(BlockedTimeInterval.resource == resource)
        time_intervals = filter_intervals_by_date(BlockedTimeInterval, time_intervals, target_date)
        for blocked_time in time_intervals.all():
            result.append(BlockedTimeUtil._convert_to_interval_to_range(target_date, blocked_time))

        return result

    @staticmethod
    def get_blocked_time_for_date_range(db_session, resource, start_date, end_date):
        diff = end_date - start_date
        result = []
        for x in range(diff.days + 1):
            date = start_date + timedelta(days=x)
            result.extend(BlockedTimeUtil.get_blocked_time_for_date(db_session, resource, date))

        return result
