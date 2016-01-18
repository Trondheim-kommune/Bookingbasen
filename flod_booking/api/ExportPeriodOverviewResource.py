# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from domain.blockedtimeutil import BlockedTimeUtil
import os
from isodate import parse_date, parse_time
from datetime import datetime, timedelta
from flask import current_app, request
from flask.ext.restful import marshal
from flask.ext.bouncer import requires, GET
from BaseResource import BaseResource, get_resource_from_web
from domain.models import Application, Slot, RepeatingSlot, StrotimeSlot, Resource
from sqlalchemy import Date, cast
from repo import get_user
from flod_common.api.external_resource_helper import ExternalResourceHelper
from api.ApplicationResource import application_fields
from api.WeeklyBlockedTimeResource import weekly_blocked_time_fields
from api.BlockedTimeIntervalResource import blocked_time_interval_fields
from flod_common.outputs.output_csv import output_csv


def get_weekday_name(day):
    days = [u'Mandag', u'Tirsdag', u'Onsdag', u'Torsdag', u'Fredag', u'Lørdag', u'Søndag']
    return days[day]


def get_person_full_name(person):
    first_name = person['first_name'] if person['first_name'] is not None else ""
    last_name = person['last_name'] if person['last_name'] is not None else ""
    return " ".join([first_name, last_name]).strip()


def get_soknad_fields_for_overview(soknad, date_object, start_time, end_time):
    result = {
        u'weekday': get_weekday_name(date_object.isoweekday() - 1),
        u'date': date_object,
        u'time': start_time + ' - ' + end_time,
        u'resource': soknad["resource"]['name'] if soknad['resource'] is not None else '',
        u'organisation': soknad["organisation"]['name'] if soknad["organisation"] is not None else '',
        u'person': get_person_full_name(soknad['person']) if soknad['person'] is not None else '',
        u'to_be_invoiced': 'Ja' if soknad['to_be_invoiced'] else 'Nei',
        u'text': soknad['text'],
        u'facilitation': get_facilitation_for_soknad(soknad),
        u'message': soknad['message'],
        u'comment': soknad['comment'],
        u'blokkering': ''
    }
    return result


def get_blocked_fields_for_overview(resource, blocked_interval, facilities):
    facility = next(facility for facility in facilities if resource == facility['uri'])
    result = {
        u'weekday': get_weekday_name(blocked_interval.get('start_time').date().isoweekday() - 1),
        u'date': blocked_interval.get('start_time').date(),
        u'time': blocked_interval.get('start_time').strftime("%H:%M") + ' - ' + blocked_interval.get('end_time').strftime("%H:%M"),
        u'resource': facility['name'],
        u'organisation': '',
        u'person': '',
        u'to_be_invoiced': '',
        u'text': '',
        u'facilitation': '',
        u'message': '',
        u'comment': '',
        u'blokkering': blocked_interval['note'] if blocked_interval['note'] else 'Enheten har reservert lokalet til eget bruk'
    }
    return result


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)


def get_facilitation_for_soknad(soknad):
    type_mappings = json.loads(open(
        os.path.join(__location__, 'type_maps.json'),
        "r"
    ).read())

    facilitations = {"amenities": soknad['amenities'],
                     "equipment": soknad['equipment'],
                     "accessibility": soknad['accessibility'],
                     "suitability": soknad['suitability'],
                     "facilitators": soknad['facilitators']}

    result = []
    for facilitation_group in facilitations:
        if facilitations[facilitation_group] is not None:
            for facility_type in facilitations[facilitation_group]:
                if facilitations[facilitation_group][facility_type] == u'on':
                    mapped_name = unicode(type_mappings[facilitation_group][facility_type])
                    result.append(mapped_name)

    facilitation = ''
    facilitation += ', '.join(result)

    if len(facilitation) != 0 and soknad['facilitation']:
        facilitation += ', '

    facilitation += soknad['facilitation'] if soknad['facilitation'] else ''
    return facilitation


def map_applications_to_organisations(applications, organisations):
    for application in applications:
        if "uri" in application["organisation"] and application["organisation"]["uri"]:
            organisation = next(organisation for organisation in organisations if
                                application["organisation"]["uri"] == organisation["uri"])
            application["organisation"] = organisation
        else:
            application["organisation"] = None


def map_applications_to_persons(applications, persons):
    for application in applications:
        person = next(person for person in persons if application["person"]["uri"] == person["uri"])
        application["person"] = person


def map_applications_to_resources(applications, resources):
    for application in applications:
        resource = next(resource for resource in resources if application["resource"]["uri"] == resource['uri'])
        application["resource"] = resource


def map_blocked_intervals_to_resources(intervals, resources):
    for interval in intervals:
        resource = next(resource for resource in resources if interval["resource"]["uri"] == resource['uri'])
        interval["resource"] = resource


def map_applications_from_query_to_pers_and_orgs_and_resources(applications_query, organisations, persons, resources):
    result = marshal(applications_query.all(), application_fields)
    map_applications_to_organisations(result, organisations)
    map_applications_to_persons(result, persons)
    map_applications_to_resources(result, resources)
    return result


def map_weekly_blocked_intervals_from_query_to_resources(weekly_blocked_intervals_query, resources):
    intervals = marshal(weekly_blocked_intervals_query.all(), weekly_blocked_time_fields)
    map_blocked_intervals_to_resources(intervals, resources)
    return intervals


def map_blocked_intervals_from_query_to_resources(blocked_intervals_query, resources):
    intervals = marshal(blocked_intervals_query.all(), blocked_time_interval_fields)
    map_blocked_intervals_to_resources(intervals, resources)
    return intervals


def add_entries_for_single_day_bookings(result, soknader):
    for soknad in soknader:
        for slot in soknad['slots']:
            start_date_object = datetime.strptime(slot['start_time'], '%Y-%m-%dT%H:%M:%S')
            end_date_object = datetime.strptime(slot['end_time'], '%Y-%m-%dT%H:%M:%S')

            new_entry = get_soknad_fields_for_overview(soknad=soknad, date_object=start_date_object.date(),
                                                       start_time=start_date_object.strftime("%H:%M"),
                                                       end_time=end_date_object.strftime("%H:%M"))
            result.append(new_entry)


def get_start_date_for_period(start_date_object, weekday):
    if start_date_object.isoweekday() <= weekday:
        start_date_for_period = start_date_object + timedelta(days=weekday - start_date_object.isoweekday())
    else:
        start_date_for_period = start_date_object + timedelta(days=7 - start_date_object.isoweekday() + weekday)
    return start_date_for_period


def add_entries_for_repeating_booking(result, repeating_bookings, start_date, end_date):
    for soknad in repeating_bookings:
        for slot in soknad['slots']:
            start_date_object = parse_date(slot['start_date'])
            end_date_object = parse_date(slot['end_date'])
            start_time = parse_time(slot['start_time'])
            end_time = parse_time(slot['end_time'])

            if start_date_object < start_date:
                start_date_object = start_date
            if end_date_object > end_date:
                end_date_object = end_date

            tmp_date = get_start_date_for_period(start_date_object, slot['week_day'])

            while tmp_date <= end_date_object:
                new_entry = get_soknad_fields_for_overview(soknad=soknad, date_object=tmp_date,
                                                           start_time=start_time.strftime("%H:%M"),
                                                           end_time=end_time.strftime("%H:%M"))
                result.append(new_entry)
                tmp_date += timedelta(weeks=1)


def add_entries_for_blocked_time(result, blocked_times, facilities):
    for resource, resource_blocked_times in blocked_times.iteritems():
        facility = next(facility for facility in facilities if resource == facility['uri'])
        for blocked_time in resource_blocked_times:
            blocked = get_blocked_fields_for_overview(resource, blocked_time, facilities)
            result.append(blocked)


def get_facilities_from_web(facilities):
    resources = []
    for facility_id in facilities:
        resource_uri = "/facilities/%s?show_not_published=True" % facility_id
        resource = get_resource_from_web(resource_uri)
        resources.append(resource)
    return resources


def get_resource_overview(facilities_ids, start_date, end_date):
    facilities = get_facilities_from_web(facilities_ids)
    facilities_uris = [facility.get('uri') for facility in facilities]
    statuses = ["Granted"]

    single_booking_query = current_app.db_session.query(Application) \
        .filter(Resource.id == Application.resource_id,
                Resource.uri.in_(facilities_uris),
                Slot.application_id == Application.id,
                Application.status.in_(statuses),
                cast(Slot.start_time, Date).between(start_date, end_date),
                cast(Slot.end_time, Date).between(start_date, end_date),
                )

    strotime_booking_query = current_app.db_session.query(Application) \
        .filter(Resource.id == Application.resource_id,
                Resource.uri.in_(facilities_uris),
                Slot.application_id == Application.id,
                Application.status.in_(statuses),
                cast(StrotimeSlot.start_time, Date).between(start_date, end_date),
                cast(StrotimeSlot.end_time, Date).between(start_date, end_date),
                )

    repeating_booking_query = current_app.db_session.query(Application) \
        .filter(Resource.id == Application.resource_id,
                Resource.uri.in_(facilities_uris),
                RepeatingSlot.application_id == Application.id,
                Application.status.in_(statuses),
                # Get all slots between start and end date
                cast(RepeatingSlot.start_date, Date) <= end_date,
                cast(RepeatingSlot.end_date, Date) >= start_date
                )

    resources = current_app.db_session.query(Resource).filter(Resource.uri.in_(facilities_uris))
    blocked_times = {}
    for resource in resources:
        blocked_times[resource.uri] = BlockedTimeUtil.get_blocked_time_for_date_range(current_app.db_session, resource, start_date, end_date)

    persons_ids = [app.person.uri.replace('/persons/', '') for app in single_booking_query] + \
                  [app.person.uri.replace('/persons/', '') for app in repeating_booking_query] + \
                  [app.person.uri.replace('/persons/', '') for app in strotime_booking_query]

    organisations_ids = [app.organisation.uri.replace('/organisations/', '') for app in single_booking_query if
                         app.organisation] + \
                        [app.organisation.uri.replace('/organisations/', '') for app in repeating_booking_query if
                         app.organisation] + \
                        [app.organisation.uri.replace('/organisations/', '') for app in strotime_booking_query if
                         app.organisation]

    current_user = get_user(request.cookies)

    persons = ExternalResourceHelper.get_persons_by_id(person_ids=persons_ids,
                                                       auth_token_username=current_user.get('id'))
    organisations = ExternalResourceHelper.get_organisations_by_id(organisation_ids=organisations_ids)

    result = []

    single_soknader = map_applications_from_query_to_pers_and_orgs_and_resources(single_booking_query, organisations, persons, facilities)
    add_entries_for_single_day_bookings(result=result, soknader=single_soknader)

    strotime_soknader = map_applications_from_query_to_pers_and_orgs_and_resources(strotime_booking_query, organisations, persons, facilities)
    add_entries_for_single_day_bookings(result=result, soknader=strotime_soknader)

    repeating_soknader = map_applications_from_query_to_pers_and_orgs_and_resources(repeating_booking_query, organisations, persons, facilities)
    add_entries_for_repeating_booking(result=result, repeating_bookings=repeating_soknader, start_date=start_date,
                                      end_date=end_date)

    add_entries_for_blocked_time(result, blocked_times, facilities)

    return result


class ExportOverviewResource(BaseResource):
    @requires(GET, 'ExportOverview')
    def get(self, facilities_ids, start, end):
        start_date = parse_date(start)
        end_date = parse_date(end)
        facilities = facilities_ids.split(",")

        resource_overview = get_resource_overview(facilities, start_date, end_date)
        sorted_overview = sorted(resource_overview, key=lambda k: (k['date'], k['resource'].lower(), k['time']))

        fieldname_mapping = OrderedDict()
        fieldname_mapping['weekday'] = 'Ukedag'
        fieldname_mapping['date'] = 'Dato'
        fieldname_mapping['resource'] = 'Lokalet'
        fieldname_mapping['time'] = 'Tid'
        fieldname_mapping['organisation'] = 'Aktør'
        fieldname_mapping['person'] = 'Person'
        fieldname_mapping['to_be_invoiced'] = 'Fakturering?'
        fieldname_mapping['text'] = 'Søknadstekst'
        fieldname_mapping['facilitation'] = 'Tilrettelegging'
        fieldname_mapping['message'] = 'Svar på søknad'
        fieldname_mapping['comment'] = 'Saksbehandlerens kommentar'
        fieldname_mapping['blokkering'] = 'Blokkering merknad'

        return output_csv(sorted_overview, 200, fieldname_mapping=fieldname_mapping)
