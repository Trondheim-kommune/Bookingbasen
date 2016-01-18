# -*- coding: utf-8 -*-

from flask.ext.restful import fields, marshal_with, abort
from flask.ext.bouncer import requires, DELETE
from flask import current_app, request
from BaseResource import ISO8601DateTime, BaseResource, get_organisation_for_uri
from domain.models import Organisation, Application, RepeatingSlot, Slot, StrotimeSlot, RepeatingSlotRequest
import datetime
from BaseApplicationResource import BaseApplicationResource

class OrganisationResource(BaseApplicationResource):

    @requires(DELETE, Organisation)
    def delete(self, organisation_id):
        # Just remove applications that are processing or pending
        organisation_uri = "/organisations/{}".format(organisation_id)
        processing_applications = current_app.db_session.query(Application).filter(
            Application.organisation.has(uri=organisation_uri),
            Application.status.in_(['Processing', 'Pending'])
        )
        for processing_application in processing_applications:
            current_app.db_session.delete(processing_application)
        current_app.db_session.commit()

        granted_applications = current_app.db_session.query(Application).filter(
            Application.organisation_id == organisation_id,
            Application.status == 'Granted'
        )
        today = datetime.date.today()
        for granted_application in granted_applications:
            if granted_application.get_type() == "single":
                # Remove single slots that are in the future
                for slot in (granted_application.single_slots + granted_application.requested_single_slots):
                    if slot.end_time.date() >= today:
                        current_app.db_session.delete(slot)
            elif granted_application.get_type() == "repeating":
                # Remove repeating slots or allocated time that are in the future
                for repeating_slot in (granted_application.requested_repeating_slots + granted_application.repeating_slots):
                    if repeating_slot.start_date >= today and repeating_slot.end_date >= today:
                        current_app.db_session.delete(repeating_slot)
                    elif repeating_slot.end_date >= today:
                        intervals = [{
                             "start": today,
                             "end":  repeating_slot.end_date
                        }]
                        periods = self.split_range_by_intervals(repeating_slot.start_date,
                                                                repeating_slot.end_date,
                                                                intervals)
                        for period in periods:
                            if isinstance(repeating_slot, RepeatingSlot):
                                current_app.db_session.add(RepeatingSlot(repeating_slot.application,
                                                                     repeating_slot.week_day,
                                                                     period['start'],
                                                                     period['end'],
                                                                     repeating_slot.start_time,
                                                                     repeating_slot.end_time))

                            if isinstance(repeating_slot, RepeatingSlotRequest):
                                granted_application.request_repeating_slot(RepeatingSlotRequest(repeating_slot.week_day,
                                                                                                period['start'],
                                                                                                period['end'],
                                                                                                repeating_slot.start_time,
                                                                                                repeating_slot.end_time))

                            current_app.db_session.delete(repeating_slot)
            elif granted_application.get_type() == "strotime":
                # Remove single slots that are in the future
                for strotime_slot in granted_application.strotime_slots:
                    if strotime_slot.end_time.date() >= today:
                        current_app.db_session.delete(strotime_slot)
        current_app.db_session.commit()

        return '', 204
