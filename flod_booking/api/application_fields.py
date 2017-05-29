#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.restful import fields

from BaseResource import ISO8601DateTime
from RepeatingSlotResource import repeating_slot_fields
from ResourceResource import resource_fields
from SlotResource import slot_fields
from common_fields import person_fields, organisation_fields

generic_slot_fields = {
    'id': fields.Integer,
    'start_date': ISO8601DateTime,  # make optional
    'end_date': ISO8601DateTime,  # make optional
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,  # make optional
}

application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'facilitation': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(generic_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'type': fields.String,
    'is_arrangement': fields.Boolean,
    'invoice_amount': fields.Integer,
    'to_be_invoiced': fields.Boolean,
    'amenities': fields.Raw,
    'equipment': fields.Raw,
    'accessibility': fields.Raw,
    'suitability': fields.Raw,
    'facilitators': fields.Raw,
    'requested_amenities': fields.Raw,
    'requested_equipment': fields.Raw,
    'requested_accessibility': fields.Raw,
    'requested_suitability': fields.Raw,
    'requested_facilitators': fields.Raw,
    'comment': fields.String,
    'requested_slots': fields.Nested(generic_slot_fields),
    'message': fields.String
}

single_application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'facilitation': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'invoice_amount': fields.Integer,
    'to_be_invoiced': fields.Boolean
}

repeating_application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'facilitation': fields.String,
    'person': fields.Nested(person_fields),
    'organisation': fields.Nested(organisation_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(repeating_slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime,
    'invoice_amount': fields.Integer,
    'to_be_invoiced': fields.Boolean
}

strotimer_application_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'person': fields.Nested(person_fields),
    'resource': fields.Nested(resource_fields),
    'requested_resource': fields.Nested(resource_fields),
    'slots': fields.Nested(slot_fields),
    'status': fields.String,
    'application_time': ISO8601DateTime
}
