# -*- coding: utf-8 -*-

from BaseResource import BaseResource
from domain.models import Settings
from flask import current_app, request
from flask.ext.bouncer import requires, ensure, GET, POST, DELETE
from flask.ext.restful import fields, marshal, abort
import datetime
from isodate import parse_datetime, parse_date


class SettingsResource(BaseResource):

    def get(self):
        settings = current_app.db_session.query(Settings).all()
        return self.convertSettingsToDict(settings)

    def convertSettingsToDict(self, arr):
        settings = {}
        for element in arr:
            if element.type == 'bool':
                settings[element.key] = element.value.lower() == "true"
            elif element.type == 'date':
                try:
                    settings[element.key] = parse_date(element.value).isoformat()
                except ValueError:
                    settings[element.key] = None
            elif element.type == 'int':
                settings[element.key] = int(element.value)

        return settings

    @requires(POST, Settings)
    def post(self):
        data = request.get_json()
        settings = current_app.db_session.query(Settings).all()

        leieform_fields = ["single_booking_allowed", "repeating_booking_allowed", "strotime_booking_allowed"]
        date_fields = ["repeating_booking_deadline", "repeating_booking_enddate", "single_booking_enddate"]

        for field in settings:
            if field.key in leieform_fields and field.key in data:
                if isinstance(data[field.key], bool):
                    field.value = str(data[field.key])
                    current_app.db_session.add(field)
                else:
                    abort(
                        400,
                        __error__=[u'Feil format på leieform felt.']
                    )
            elif field.key in date_fields and field.key in data and data[field.key]:
                try:
                    field.value = str(parse_date(data[field.key]))
                    current_app.db_session.add(field)
                except ValueError:
                    abort(
                        400,
                        __error__=[u'Søknadsfrist for lån må være dato.']
                    )

        current_app.db_session.commit()

        return self.convertSettingsToDict(settings), 201