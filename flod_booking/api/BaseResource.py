import os

from flask import current_app
from flask.ext import restful
from flask.ext.restful import fields
from isodate import parse_date, ISO8601Error
from sqlalchemy.orm.exc import NoResultFound
from datetime import timedelta

from uri_resource_getter import UriResourceGetter
from api_exceptions import ApiException
from domain.models import Resource, Organisation, Person, Application, UmbrellaOrganisation

RESOURCES_URL = os.environ.get('RESOURCES_URL', 'http://localhost:5000')
ORGANISATIONS_URL = os.environ.get('ORGANISATIONS_URL', 'http://localhost:1338')

resource_getter = UriResourceGetter(RESOURCES_URL + '/api/v1', Resource, "resource")
organisation_getter = UriResourceGetter(ORGANISATIONS_URL + '/api/v1', Organisation, "organisation")
umbrella_organisation_getter = UriResourceGetter(ORGANISATIONS_URL + '/api/v1', UmbrellaOrganisation, "umbrella_organisation")
person_getter = UriResourceGetter(ORGANISATIONS_URL + '/api/v1', Person, "person")


def get_umbrella_organisation_for_uri(uri):
    return umbrella_organisation_getter.get_for_uri(uri)


def get_umbrella_organisation_from_web(uri):
    return umbrella_organisation_getter.get_from_web(uri)


def get_organisation_for_uri(uri, cookies=None):
    return organisation_getter.get_for_uri(uri, cookies=cookies)


def get_organisation_from_web(uri, cookies=None):
    return organisation_getter.get_from_web(uri, cookies)


def get_person_for_uri(uri):
    return person_getter.get_for_uri(uri)


def get_person_from_web(uri, cookies=None):
    return person_getter.get_from_web(uri)


def get_resource_for_uri(uri):
    return resource_getter.get_for_uri(uri)


def get_resource_from_web(uri, cookies=None):
    return resource_getter.get_from_web(uri, cookies)


class ISO8601DateTime(fields.Raw):
    def format(self, value):
        return value.isoformat()


def get_application_for_id(application_id):
    application = current_app.db_session.query(Application).get(application_id)
    if not application:
        message = "No application found with id %d." % application_id
        cls.raiseException(make_error_dict(message), 404)
    return application


def make_error_dict(error_message):
    return {"__error__": [error_message]}


def verify_request_contains_mandatory_fields(data, mandatory_fields):
    for field in mandatory_fields:
        if field not in data:
            raise ApiException(make_error_dict("Missing mandatory field: %s" % field), 400)


class BaseResource(restful.Resource):
    @classmethod
    def get_first_occurrence(cls, week_day, start_date):
        d = start_date
        delta = timedelta(days=1)
        while d.isoweekday() != week_day:
            d += delta
        return d

    @classmethod
    def get_last_occurrence(cls, week_day, start_date, end_date):
        d = end_date
        delta = timedelta(days=1)
        while d.isoweekday() != week_day:
            d -= delta
            if d < start_date: return None
        return d

    @classmethod
    def split_range_by_intervals(cls, start, end, intervals):
        periods = []
        current_start = start
        for i in range(0, len(intervals)):
            interval = intervals[i]

            # In the start
            if i == 0:
                # Add a new period if the first interval
                # starts after the original start time.
                # The period would then have a duration
                # from the original start to the first interval start.
                if interval['start'] > start:
                    periods.append({
                        'start': start,
                        'end': interval['start']
                    })
                current_start = interval['end']

            # In the middle
            if i > 0 and i < len(intervals):
                # Add a new period if the interval
                # starts after the current start.
                # The period would then have a duration
                # from the current start to the interval start.
                if current_start < interval['start']:
                    periods.append({
                        'start': current_start,
                        'end': interval['start']
                    })
                if interval['end'] > current_start:
                    current_start = interval['end']

            # In the end
            if i == len(intervals) - 1:
                # Add a new period if the original end
                # ends after the last interval ends.
                # The period would then have a duration
                # from the last interval end to
                # the original end.
                if interval['end'] < end:
                    periods.append({
                        'start': interval['end'],
                        'end': end
                    })

        # Just return the original range if
        # there are zero periods generated
        if len(periods) == 0:
            return [{
                'start': start,
                'end': end
            }]
        else:
            return periods

    @staticmethod
    def get_resource_for_id(resource_id):
        return current_app.db_session.query(Resource).filter(Resource.id == resource_id).one()

    @staticmethod
    def raiseException(message, status_code):
        raise ApiException(message, status_code)

    @classmethod
    def get_resource_with_id_or_uri(cls, resource_id, resource_uri):
        try:
            if resource_id:
                return cls.get_resource_for_id(resource_id)
            else:
                return get_resource_for_uri(resource_uri)
        except NoResultFound:
            cls.raiseException(make_error_dict("No resource found."), 404)

    @classmethod
    def parse_date_from_args(cls, data, key):
        try:
            return parse_date(data[key])
        except ISO8601Error, exception:
            cls.raiseException(make_error_dict(str(exception)), 404)

    @classmethod
    def parse_date_range_from_dict(cls, data):
        verify_request_contains_mandatory_fields(data, ["start_date", "end_date"])
        try:
            start_date = parse_date(data["start_date"])
            end_date = parse_date(data["end_date"])
            return (start_date, end_date)
        except ISO8601Error, exception:
            cls.raiseException(make_error_dict(str(exception)), 404)

    @classmethod
    def parse_date_range_from_args(cls, request):
        return cls.parse_date_range_from_dict(request.args)

    @classmethod
    def get_object_by_id(cls, item_id):
        try:
            return current_app.db_session.query(cls.t).filter(cls.t.id == item_id).one()
        except NoResultFound:
            message = "No %s found with id %d." % (cls.type_name, item_id)
            cls.raiseException(make_error_dict(message), 404)
