# -*- coding: utf-8 -*-

from flask import request, current_app
from datetime import datetime
from flask.ext.restful import marshal_with, fields, abort
from sqlalchemy import and_, or_, Date, Time, cast, extract, tuple_
from sqlalchemy.orm import aliased

from api_exceptions import format_exception
from BaseResource import BaseResource, ISO8601DateTime
from SlotsForWeekResource import get_display_name
from domain.models import (RepeatingSlot, Application, RepeatingSlotRequest,
                           Resource)

week_repeating_slot_fields = {
    'start_date' : ISO8601DateTime,
    'end_date' : ISO8601DateTime,
    'start_time' : ISO8601DateTime,
    'end_time' : ISO8601DateTime,
    'week_day' : fields.Integer,
    'status': fields.String,
    'display_name': fields.String,
    'application_id': fields.Integer,
    'application_type': fields.String,
    'organisation_uri': fields.String
}

class WeeklyRepeatingSlotsForResource(BaseResource):
    method_decorators = [format_exception]


    # Get Alembic stuff to work, add a proper relation from RepeatingSlot to Application,
    # and then merge get_repeating and get_requested_slots (the only difference now is
    # ~RepeatingSlot.application.in_() vs. ~RepeatingSlotRequest.application_id.in_()
    def get_repeating(self, resource, except_applications, start_date, end_date, statuses):
        query = current_app.db_session.query(RepeatingSlot)
        objects = query.filter(Application.resource == resource,
                               RepeatingSlot.application_id == Application.id,
                               Application.status.in_(statuses))

        if except_applications:
            objects = objects.filter(
                ~RepeatingSlot.application_id.in_(except_applications)
            )

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

        return objects.all()

    def get_requested_slots(self, resource, except_applications, start_date, end_date):
        query = current_app.db_session.query(RepeatingSlotRequest)

        objects = query.filter(
            RepeatingSlotRequest.application.has(resource_id=resource.id)
        )

        objects = objects.filter(
            RepeatingSlotRequest.application.has(status="Pending")
        )

        if except_applications:
            objects = objects.filter(
                ~RepeatingSlotRequest.application_id.in_(except_applications)
            )

        objects = objects.filter(
            or_(
                tuple_(
                    RepeatingSlotRequest.start_date, RepeatingSlotRequest.end_date
                ).op('overlaps')(
                    tuple_(
                        cast(start_date, Date), cast(end_date, Date)
                    )
                ),
                or_(
                    # First range ends on the start date of the second
                    RepeatingSlotRequest.end_date == cast(start_date, Date),
                    # Second range ends on the start date of the first
                    cast(end_date, Date) == RepeatingSlotRequest.start_date
                )
            )
        )

        return objects.all()

    @marshal_with(week_repeating_slot_fields)
    def get(self):
        resource_uri = request.args.get('resource_uri')
        except_application = request.args.get('except')

        if not "start_date" in request.args or not "end_date" in request.args:
            abort(404, __error__ = [ "start and end date must be set!" ])

        start_date =  datetime.strptime(request.args["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.args["end_date"], "%Y-%m-%d").date()

        if "status" in request.args:
            statuses = [request.args["status"]]
        else:
            statuses = ["Pending", "Processing", "Granted"]

        resource = self.get_resource_with_id_or_uri(None, resource_uri)

        except_applications = []
        if except_application:
            except_applications.append(int(except_application))

        result = []
        slots = self.get_repeating(resource, except_applications, start_date, end_date, statuses)

        #first we get all repeating slots
        for slot in slots:

            application = current_app.db_session.query(Application).filter(
                Application.id == slot.application_id
            ).one()

            display_name = get_display_name(application)
            except_applications.append(slot.application.id)

            result.append({
                'start_time': slot.start_time,
                'end_time': slot.end_time,
                'start_date': slot.start_date,
                'end_date': slot.end_date,
                'week_day': slot.week_day,
                'id': slot.id,
                'display_name': display_name,
                'application_id': application.id,
                'application_type': application.type,
                'status': slot.application.status,
                'organisation_uri': application.organisation.uri if application.organisation else None
                })


        #then, if pending statuses should be included, we get requested slots for
        # the applications that doesn't have slots (i.e. just requested)
        if "Pending" in statuses:
            requested_slots = self.get_requested_slots(resource, except_applications, start_date, end_date)
            for requested_slot in requested_slots:
                result.append({
                    'start_time': requested_slot.start_time,
                    'end_time': requested_slot.end_time,
                    'start_date': requested_slot.start_date,
                    'end_date': requested_slot.end_date,
                    'week_day': requested_slot.week_day,
                    'id': requested_slot.id,
                    'display_name': get_display_name(requested_slot.application),
                    'application_id': requested_slot.application_id,
                    'application_type': requested_slot.application.type,
                    'status': 'Pending',
                    'organisation_uri': requested_slot.application.organisation.uri if requested_slot.application.organisation else None
                    })

        return result, 200
