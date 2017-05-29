#!/usr/bin/env python
# -*- coding: utf-8 -*-

from domain.models import Application
from flask.ext.bouncer import requires, GET
from flask.ext.restful import fields, marshal

from ArrangementBaseResource import ArrangementBaseResource
from BaseResource import ISO8601DateTime
from ResourceResource import resource_fields
from common_fields import person_fields, organisation_fields

generic_slot_fields = {
    'id': fields.Integer,
    'start_date': ISO8601DateTime,
    'end_date': ISO8601DateTime,
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,
}

application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(generic_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'type': fields.String
}


class ArrangementConflictsResource(ArrangementBaseResource):
    t = Application
    type_name = "application"

    @requires(GET, 'ArrangementConflict')
    def get(self, application_id=None):
        arrangement = self.get_arrangement(application_id)
        return marshal(self.get_affected_applications(arrangement), application_fields)
