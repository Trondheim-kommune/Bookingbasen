# -*- coding: utf-8 -*-

from flask.ext import restful
from flask.ext.bouncer import requires, ensure, PUT
from flask import current_app, request
from flask.ext.restful import fields, marshal_with
from sqlalchemy import and_, or_
from datetime import datetime

from domain.models import Resource, Rammetid, UmbrellaOrganisation, RammetidSlot
from api_exceptions import format_exception
from BaseResource import get_resource_for_uri, \
    verify_request_contains_mandatory_fields

resource_fields = {
    'id': fields.Integer,
    'uri': fields.String,
    'auto_approval_allowed': fields.Boolean,
    'single_booking_allowed': fields.Boolean,
    'repeating_booking_allowed': fields.Boolean
}


class ResourceResource(restful.Resource):
    method_decorators = [format_exception]

    def get_resource(self, resource_id, resource_uri):
        if resource_id:
            return current_app.db_session.query(
                Resource
            ).filter(Resource.id == resource_id).one()
        if resource_uri:
            return get_resource_for_uri("/%s" % resource_uri)

    @marshal_with(resource_fields)
    def get(self, resource_id=None, resource_uri=None):
        if resource_id or resource_uri:
            return self.get_resource(resource_id, resource_uri)
        else:
            resources = current_app.db_session.query(Resource)
            if "booking_type" in request.args and \
                            request.args["booking_type"] == "auto_approval_allowed":
                resources = resources.filter(
                    Resource.auto_approval_allowed == True
                )

            if "booking_type" in request.args and \
                            request.args["booking_type"] == "repeating_booking_allowed":
                resources = resources.filter(
                    Resource.repeating_booking_allowed == True
                )

            if "umbrella_organisation_uri" in request.args:
                resources = resources.filter(
                    Rammetid.resource_id == Resource.id,
                    UmbrellaOrganisation.id == Rammetid.umbrella_organisation_id,
                    UmbrellaOrganisation.uri == request.args["umbrella_organisation_uri"],
                    RammetidSlot.rammetid_id == Rammetid.id
                )
                if "start_date" in request.args and "end_date" in request.args:
                    start_date = datetime.strptime(request.args["start_date"], "%Y-%m-%d").date()
                    end_date = datetime.strptime(request.args["end_date"], "%Y-%m-%d").date()
                    resources = resources.filter(or_(
                        and_(
                            start_date >= RammetidSlot.start_date,
                            start_date <= RammetidSlot.end_date
                        ),
                        and_(
                            end_date >= RammetidSlot.start_date,
                            end_date <= RammetidSlot.end_date
                        ),
                    ))
            return resources.order_by(Resource.id).all()

    @requires(PUT, Resource)
    @marshal_with(resource_fields)
    def put(self, resource_id=None, resource_uri=None):
        data = request.get_json()

        mandatory_fields = ["auto_approval_allowed", "single_booking_allowed",
                            "repeating_booking_allowed"]
        verify_request_contains_mandatory_fields(data, mandatory_fields)

        resource = self.get_resource(resource_id, resource_uri)
        ensure(PUT, resource)
        # Update the allowed booking types..
        resource.auto_approval_allowed = data["auto_approval_allowed"]
        resource.single_booking_allowed = data["single_booking_allowed"]
        resource.repeating_booking_allowed = data["repeating_booking_allowed"]

        current_app.db_session.add(resource)
        current_app.db_session.commit()
        current_app.db_session.refresh(resource)
        return resource
