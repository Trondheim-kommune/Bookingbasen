# -*- coding: utf-8 -*-
import os
from flask import current_app, request
from flask.ext.restful import fields, marshal_with, abort
from flask.ext.bouncer import requires, POST
from isodate import parse_datetime
from BaseResource import ISO8601DateTime, get_resource_from_web, \
    get_person_from_web
from BaseApplicationResource import BaseApplicationResource
from domain.models import StrotimeSlot, Application
from sqlalchemy import and_, or_

strotimer_application_notifications_fields = {
    'id': fields.Integer,    
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'application_id': fields.Integer,
    'email_address': fields.String,
    'resource_name': fields.String,
    'person_name': fields.String
}

class StrotimeApplicationNotificationsResource(BaseApplicationResource):

    @requires(POST, 'StrotimeApplicationNotification')
    @marshal_with(strotimer_application_notifications_fields)
    def post(self):
        data = request.get_json()        
        start_time = data["start_time"]
        end_time = data["end_time"]             
        if start_time is None or end_time is None:
            abort(400)
        strotime_slots = self.get_strotime_slots(start_time, end_time)
        result = []
        for strotime_slot in strotime_slots:            
            personJSON = get_person_from_web(strotime_slot.application.person.uri)                                            
            resourceJSON = get_resource_from_web(strotime_slot.application.resource.uri)                                    
            result.append({             
                'id': strotime_slot.id,
                'start_time': strotime_slot.start_time,
                'end_time': strotime_slot.end_time,                
                'application_id': strotime_slot.application.id,
                'resource_name': resourceJSON['name'],
                'email_address': personJSON['email_address'],
                'person_name': personJSON['first_name'] + " " + personJSON['last_name']
            })
        return result, 201

    def get_strotime_slots(self, start_time, end_time):
        query = current_app.db_session.query(StrotimeSlot)
        statuses = ["Granted"]
        objects = query.filter(StrotimeSlot.application_id == Application.id, 
                               Application.status.in_(statuses))
        objects = objects.filter(
            and_(
                and_(
                    StrotimeSlot.start_time >=  start_time,
                    StrotimeSlot.start_time <=  end_time
                ),
                and_(
                    StrotimeSlot.end_time >=  start_time,
                    StrotimeSlot.end_time <=  end_time
                )
            )
        )
        return objects.all()
