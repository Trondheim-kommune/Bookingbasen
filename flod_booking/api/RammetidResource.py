#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app, request
from flask.ext.restful import fields, marshal, abort
from flask.ext.bouncer import requires, POST, PUT, DELETE
from api.BaseApplicationResource import BaseApplicationResource
from isodate import parse_date, parse_time
from api_exceptions import format_exception
from domain.models import Rammetid, RammetidSlot
from BaseResource import ISO8601DateTime, get_resource_for_uri, get_umbrella_organisation_for_uri
from ResourceResource import resource_fields
from common_fields import umbrella_organisation_fields
from BaseResource import BaseResource

generic_slot_fields = {
    'id': fields.Integer,
    'start_date': ISO8601DateTime,
    'end_date': ISO8601DateTime,
    'start_time': ISO8601DateTime,
    'end_time': ISO8601DateTime,
    'week_day': fields.Integer,
}

rammetid_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'umbrella_organisation': fields.Nested(umbrella_organisation_fields),
    'resource': fields.Nested(resource_fields),
    'rammetid_slots': fields.Nested(generic_slot_fields),
    'status': fields.String,
    'create_time': ISO8601DateTime
}


def parse_repeating_slot(data):
    start_date = parse_date(data["start_date"])
    end_date = parse_date(data["end_date"])
    start_time = parse_time(data["start_time"])
    end_time = parse_time(data["end_time"])
    week_day = data["week_day"]
    return RammetidSlot(
        week_day,
        start_date,
        end_date,
        start_time,
        end_time
    )


class RammetidResource(BaseResource):
    t = Rammetid
    type_name = "rammetid"
    method_decorators = [format_exception]

    def get(self, rammetid_id=None):
        if rammetid_id:
            rammetid = self.get_object_by_id(rammetid_id)
            return marshal(rammetid, rammetid_fields)
        else:
            resource_uri = request.args.get('resource_uri')
            umbrella_organisation_uri = request.args.get('umbrella_organisation_uri')
            if "only_periods" in request.args and resource_uri and umbrella_organisation_uri:
                resource = self.get_resource_with_id_or_uri(None, resource_uri)
                umbrella_organisation = get_umbrella_organisation_for_uri(umbrella_organisation_uri)
                rammetids = current_app.db_session.query(RammetidSlot.start_date.label('start_date'), RammetidSlot.end_date.label('end_date')) \
                    .filter(Rammetid.id == RammetidSlot.rammetid_id, Rammetid.resource_id == resource.id, Rammetid.umbrella_organisation_id == umbrella_organisation.id) \
                    .distinct(RammetidSlot.start_date, RammetidSlot.end_date) \
                    .group_by(RammetidSlot.start_date, RammetidSlot.end_date) \
                    .order_by(RammetidSlot.start_date, RammetidSlot.end_date)

                res = [dict(zip(['start_date', 'end_date'], r)) for r in rammetids.all()]

                return marshal(res, {'start_date': ISO8601DateTime, 'end_date': ISO8601DateTime})
            else:
                rammetids = current_app.db_session.query(Rammetid).order_by(Rammetid.id)
                return marshal(rammetids.all(), rammetid_fields)

    @requires(POST, Rammetid)
    def post(self):
        data = request.get_json()

        resource_data = data.get("resource", None)
        if resource_data:
            resource_uri = resource_data["uri"]
            resource = get_resource_for_uri(resource_uri)
            if not resource:
                abort(403, __error__=[u'Ressursen ble ikke funnet.'])
        else:
            abort(403, __error__=[u'Data om ressursen mangler.'])

        umbrella_organisation_data = data.get("umbrella_organisation", None)
        if umbrella_organisation_data:
            umbrella_organisation_uri = umbrella_organisation_data["uri"]
            umbrella_organisation = get_umbrella_organisation_for_uri(umbrella_organisation_uri)
            if not umbrella_organisation:
                abort(403, __error__=[u'Paraplyorganisasjonen ble ikke funnet.'])
        else:
            abort(403, __error__=[u'Data om paraplyorganisasjonen mangler.'])

        rammetid = Rammetid(umbrella_organisation, resource)

        rammetid_slots_data = data.get("rammetid_slots", None)
        if rammetid_slots_data:
            for rammetid_slot in rammetid_slots_data:
                rammetid_slot_parsed = parse_repeating_slot(rammetid_slot)
                if BaseApplicationResource.is_conflict_rammetid(resource, rammetid_slot_parsed.start_date, rammetid_slot_parsed.end_date, rammetid_slot_parsed.week_day,
                                                                rammetid_slot_parsed.start_time, rammetid_slot_parsed.end_time):
                    abort(
                        400,
                        __error__=[u'Tiden er ikke tilgjengelig']
                    )
                if BaseApplicationResource.is_conflict_blocked_time(resource, rammetid_slot_parsed.start_date, rammetid_slot_parsed.end_date, rammetid_slot_parsed.week_day,
                                                                    rammetid_slot_parsed.start_time, rammetid_slot_parsed.end_time):
                    abort(
                        400,
                        __error__=[u'Tiden er blokkert']
                    )
                rammetid.add_rammetid_slot(rammetid_slot_parsed)

        current_app.db_session.add(rammetid)
        current_app.db_session.commit()
        current_app.db_session.refresh(rammetid)

        return marshal(rammetid, rammetid_fields), 201

    @requires(PUT, Rammetid)
    def put(self, rammetid_id):
        data = request.get_json()

        rammetid = self.get_object_by_id(rammetid_id)

        status = data.get("status", None)

        resource_data = data.get("resource", None)
        if resource_data:
            resource_uri = resource_data["uri"]
            resource = get_resource_for_uri(resource_uri)
            if not resource:
                abort(403, __error__=[u'Ressursen ble ikke funnet.'])
        else:
            abort(403, __error__=[u'Data om ressursen mangler.'])

        # The rammetid might have been
        # moved to a different resource
        rammetid.resource = resource

        # The rammtid status might
        # have been changed
        rammetid.status = status

        rammetid_slots_data = data.get("rammetid_slots", None)
        if rammetid_slots_data:
            for rammetid_slot in rammetid_slots_data:
                rammetid_slot_parsed = parse_repeating_slot(rammetid_slot)
                if BaseApplicationResource.is_conflict_rammetid(resource, rammetid_slot_parsed.start_date, rammetid_slot_parsed.end_date, rammetid_slot_parsed.week_day,
                                                                rammetid_slot_parsed.start_time, rammetid_slot_parsed.end_time):
                    abort(
                        400,
                        __error__=[u'Tiden er ikke tilgjengelig']
                    )
                if BaseApplicationResource.is_conflict_blocked_time(resource, rammetid_slot_parsed.start_date, rammetid_slot_parsed.end_date, rammetid_slot_parsed.week_day,
                                                                    rammetid_slot_parsed.start_time, rammetid_slot_parsed.end_time):
                    abort(
                        400,
                        __error__=[u'Tiden er blokkert']
                    )

                rammetid.add_rammetid_slot(rammetid_slot_parsed)

        current_app.db_session.add(rammetid)
        current_app.db_session.commit()
        current_app.db_session.refresh(rammetid)

        return marshal(rammetid, rammetid_fields)

    @requires(DELETE, Rammetid)
    def delete(self, rammetid_id):
        rammetid = self.get_object_by_id(rammetid_id)
        current_app.db_session.delete(rammetid)
        current_app.db_session.commit()
        return "", 204
