# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date
from datetime import timedelta
from flask.ext.restful import fields, marshal, abort
from flask import current_app, request
from sqlalchemy import and_, Date, cast, or_, tuple_
import werkzeug

from domain.models import Application, Slot, SlotRequest, \
    RepeatingSlot, RepeatingSlotRequest, StrotimeSlot
from api_exceptions import format_exception
from BaseResource import (BaseResource, ISO8601DateTime,
                          get_organisation_from_web, get_person_from_web)
from repo import get_user, has_role


def get_start_and_end_date_from_week_and_year(year, week):
    start_date = get_date_from_weekday_week_and_year(1, week, year)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def get_date_from_weekday_week_and_year(week_day, week_number, year):
    d = date(year, 1, 4)  # The Jan 4th must be in week 1  according to ISO
    return d + timedelta(weeks=(week_number-1), days=-d.weekday()+(week_day-1))

week_exploded_slot_fields = {
    'uri': fields.String,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'status': fields.String,
    'display_name': fields.String,
    'application_id': fields.Integer,
    'application_type': fields.String,
    'is_arrangement': fields.Boolean,
}

week_exploded_slot_fields_applicant = dict(
    week_exploded_slot_fields.items() +
    [('applicant_email', fields.String),
     ('applicant_name', fields.String)]
)


def get_display_name(application):

    if application.organisation:
        try:
            org = get_organisation_from_web(application.organisation.uri)
            return org.get('name')
        except werkzeug.exceptions.NotFound:
            return u'Ad-hoc aktør'


    user = get_user(request.cookies)
    show_person = user is not None and has_role(user, 'flod_saksbehandlere')
    if show_person:
        person = get_person_from_web(application.person.uri)
        return '%s, %s' % (person.get('last_name', ''), person.get('first_name', ''))
    return "Privatperson"


class SlotsForWeekResource(BaseResource):
    method_decorators = [format_exception]

    @classmethod
    def get_by_resource_and_status(cls, type, resource, statuses=None):
        query = current_app.db_session.query(type)
        objects = query.filter(
            type.application_id == Application.id,
            Application.resource == resource
        )
        if statuses:
            objects = objects.filter(
                Application.status.in_(statuses)
            )
        return objects

    @classmethod
    def filter_by_applications_object(cls, type, objects, applications):
        '''
        this is used when relationship to application is properly mapped
        '''
        if applications:
            return objects.filter(
                ~type.application_id.in_(applications)
            )
        return objects


    @classmethod
    def filter_single_by_time(cls, type, objects, year=None, week_number=None, day=None):

        assert (week_number and year) or day
        start_date, end_date = None, None

        if year and week_number:
            start_date, end_date = get_start_and_end_date_from_week_and_year(
                year,
                week_number
            )
        if day:
            start_date = day
            end_date = day

        objects = objects.filter(
            or_(
                tuple_(
                    cast(type.start_time, Date), cast(type.end_time, Date)
                ).op('overlaps')(
                    tuple_(
                        start_date, end_date
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    cast(type.end_time, Date) == start_date,
                    # Second range ends on the start date of the first
                    end_date == cast(type.start_time, Date)
                )
            )
        )

        return objects

    @classmethod
    def filter_repeating_by_time(cls, type, objects, year=None, week_number=None, day=None):

        assert (week_number and year) or day
        start_date, end_date = None, None

        if year and week_number:
            start_date, end_date = get_start_and_end_date_from_week_and_year(
                year,
                week_number
            )
        if day:
            start_date = day
            end_date = day
            objects = objects.filter(
                type.week_day == day.isoweekday()
            )

        objects = objects.filter(
            or_(
                tuple_(
                    type.start_date, type.end_date
                ).op('overlaps')(
                    tuple_(
                        start_date, end_date
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    type.end_date == start_date,
                    # Second range ends on the start date of the first
                    end_date == type.start_date
                )
            )
        )
        return objects

    @classmethod
    def create_slot_from_single(cls, slot, status, type, application):
        return {
          #  'uri': "/%s/%s" % (type, slot.id),
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'status': status,
            'display_name': get_display_name(application),
            'application_id': application.id,
            'application_type': type,
            'application': application,
            'is_arrangement': application.is_arrangement
        }

    @classmethod
    def create_slot_from_repeating(cls, slot, status, application, slot_date):
        return {
           # 'uri': "/%s/%s" % (type, slot.id),
            'start_time' : datetime.combine(slot_date, slot.start_time),
            'end_time' : datetime.combine(slot_date, slot.end_time),
            'status': status,
            'display_name': get_display_name(application),
            'application_id': application.id,
            'application_type': 'repeating',
            'application': application
            }

    def get_repeating_slots(self, resource, except_applications, statuses, year, week_number, day):
        objects = self.get_by_resource_and_status(
            RepeatingSlot,
            resource,
            statuses
        )
        objects = self.filter_by_applications_object(
            RepeatingSlot,
            objects,
            except_applications
        )
        objects = self.filter_repeating_by_time(
            RepeatingSlot,
            objects,
            year,
            week_number,
            day
        )

        exploded = []
        for slot in objects.all():
            if not day:
                slot_date = get_date_from_weekday_week_and_year(slot.week_day, week_number, year)
            else:
                slot_date = day.date()

            if  slot.start_date <= slot_date <= slot.end_date:
                except_applications.append(slot.application_id)
                exploded.append(self.create_slot_from_repeating(
                    slot,
                    slot.application.status,
                    slot.application,
                    slot_date
                ))


        if "Pending" in statuses:
            objects = self.get_by_resource_and_status(
                RepeatingSlotRequest,
                resource
            )
            objects = self.filter_by_applications_object(
                RepeatingSlotRequest,
                objects,
                except_applications
            )
            objects = self.filter_repeating_by_time(
                RepeatingSlotRequest,
                objects,
                year,
                week_number,
                day
            )

            objects = objects.filter(
                RepeatingSlotRequest.application_id == Application.id,
                Application.status=='Pending'
            )

            for requested_slot in objects.all():

                if not day:
                    slot_date = get_date_from_weekday_week_and_year(requested_slot.week_day, week_number, year)
                else:
                    slot_date = day

                if  requested_slot.start_date <= slot_date <= requested_slot.end_date:
                    exploded.append(self.create_slot_from_repeating(
                        requested_slot,
                        requested_slot.application.status,
                        requested_slot.application,
                        slot_date
                    ))
        return exploded

    def get_slots(self, resource, except_applications, statuses, year, week_number, day):

        objects = self.get_by_resource_and_status(Slot, resource, statuses)
        objects = self.filter_by_applications_object(
            Slot,
            objects,
            except_applications
        )
        objects = self.filter_single_by_time(Slot, objects, year, week_number, day)

        result = []
        for slot in objects.all():
            except_applications.append(slot.application_id)
            result.append(self.create_slot_from_single(
                slot,
                slot.application.status,
                'single',
                slot.application
            ))

        if "Pending" in statuses:
            objects = self.get_by_resource_and_status(SlotRequest, resource)
            objects = self.filter_by_applications_object(
                SlotRequest,
                objects,
                except_applications
            )
            objects = self.filter_single_by_time(
                SlotRequest,
                objects,
                year,
                week_number,
                day
            )

            objects = objects.filter(
                SlotRequest.application_id == Application.id,
                Application.status=='Pending'
            )

            for requested_slot in objects.all():
                result.append(self.create_slot_from_single(
                    requested_slot,
                    requested_slot.application.status,
                    'single',
                    requested_slot.application
                ))
        return result

    def get_strotime_slots(self, resource, year, week_number, day):

        objects = self.get_by_resource_and_status(StrotimeSlot, resource)
        objects = self.filter_single_by_time(StrotimeSlot, objects, year, week_number, day)

        result = []
        for slot in objects.all():
            result.append(self.create_slot_from_single(
                slot,
                slot.application.status,
                'strotime',
                slot.application
            ))
        return result

    def get_applicant(self, slot):
        application = slot['application']
        if application.organisation is not None:
            org = get_organisation_from_web(application.organisation.uri)
            return (org.get('name'), org.get('email_address'))
        if application.person is not None:
            person = get_person_from_web(application.person.uri)
            name = u'{}, {}'.format(person.get('last_name', ''),
                                    person.get('first_name', ''))
            return (name, person.get('email_address'))
        return None

    def get(self):

        year = None
        if "year" in request.args:
            year = int(request.args.get('year'))
        week_number = None
        if "week" in request.args:
            week_number = int(request.args.get('week'))
        day = None
        if "day" in request.args:
            day = datetime.strptime(request.args.get('day'), '%Y-%m-%d')

        resource_uri = request.args.get('resource_uri')
        except_application = request.args.get('except')

        if not (year and week_number) and not day:
            abort(404)

        if "status" in request.args:
            statuses = [request.args["status"]]
        else:
            statuses = ["Pending", "Processing", "Granted"]

        resource = self.get_resource_with_id_or_uri(None, resource_uri)

        except_applications = []
        if except_application:
            except_applications.append(except_application)

        single = self.get_slots(
            resource,
            except_applications,
            statuses,
            year,
            week_number,
            day
        )
        repeating = self.get_repeating_slots(
            resource,
            except_applications,
            statuses,
            year,
            week_number,
            day
        )

        strotimer = self.get_strotime_slots(
            resource,
            year,
            week_number,
            day
        )

        slots = single + repeating + strotimer


        user = get_user(request.cookies)
        if user is not None and has_role(user, 'flod_saksbehandlere'):
            for slot in slots:
                applicant = self.get_applicant(slot)
                if applicant is not None:
                    name, email = applicant
                    slot['applicant_email'] = email
                    slot['applicant_name'] = name
            return marshal(slots, week_exploded_slot_fields_applicant), 200

        return marshal(slots, week_exploded_slot_fields), 200
