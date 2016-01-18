# -*- coding: utf-8 -*-

from flask.ext.restful import fields, marshal_with, abort
from flask.ext.bouncer import requires, ensure, GET, POST, DELETE
from flask import current_app, request

from BaseResource import ISO8601DateTime, BaseResource, get_organisation_for_uri
from common_fields import organisation_fields
from domain.models import OrganisationInternalNote

organisation_internal_note_fields = {
    'id': fields.Integer,
    'auth_id' : fields.String,
    'organisation' : fields.Nested(organisation_fields),
    'text': fields.String,
    'create_time' : ISO8601DateTime,
    }

class OrganisationInternalNotesResource(BaseResource):
    t = OrganisationInternalNote
    type_name = "organisations_internal_notes"

    @requires(GET, OrganisationInternalNote)
    @marshal_with(organisation_internal_note_fields)
    def get(self, organisation_id = None, note_id=None):
        if note_id is not None:
            note = current_app.db_session.query(
                OrganisationInternalNote
            ).get(note_id)
            if note is None:
                abort(404)
            return note
        else:
            notes = current_app.db_session.query(
                OrganisationInternalNote
            ).filter(
                OrganisationInternalNote.organisation.has(
                    uri="/organisations/{}".format(organisation_id))
            )
            return notes.all()

    @requires(POST, OrganisationInternalNote)
    @marshal_with(organisation_internal_note_fields)
    def post(self, organisation_id=None, note_id=None):
        data = request.get_json()

        text = data["text"]

        organisation_data = data.get("organisation", None)
        if organisation_data:
            organisation_uri = organisation_data["uri"]
            organisation = get_organisation_for_uri(organisation_uri)
        else:
            organisation = None

        auth_id = data["auth_id"]

        note = OrganisationInternalNote(organisation, text, auth_id)

        current_app.db_session.add(note)
        current_app.db_session.commit()
        current_app.db_session.refresh(note)

        return note, 201

    @requires(DELETE, OrganisationInternalNote)
    @marshal_with(organisation_internal_note_fields)
    def delete(self, organisation_id=None, note_id=None):
        if note_id is None:
            abort(400)
        note = current_app.db_session.query(
            OrganisationInternalNote
        ).get(note_id)
        if note is None:
            abort(404)

        current_app.db_session.delete(note)
        current_app.db_session.commit()

        return '', 204
