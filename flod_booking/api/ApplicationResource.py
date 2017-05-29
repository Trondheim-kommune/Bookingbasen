#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from base64 import b64encode

import datetime
from arkiv.arkivclient import ArkivDBClient, WSSak, WSAdressat, WSDokument, WSJournalpost
from celery_tasks.email_tasks import send_email_task, send_email_with_csv_task
from domain.erv import erv_person, erv_organisation
from domain.models import Application, Resource, Organisation, Slot, RepeatingSlot, Person, FesakSak, StrotimeSlot
from flask import current_app, request, render_template
from flask.ext.bouncer import requires, ensure, GET, PUT, DELETE
from flask.ext.restful import marshal, abort
from flod_common.session.utils import unsign_auth_token, verify_superuser_auth_token
from isodate import parse_datetime, parse_date, parse_time
from repo import get_user, has_role
from sqlalchemy import or_
from util.email import format_application_status_for_email, format_slots_for_email

from BaseApplicationResource import BaseApplicationResource
from BaseResource import get_resource_for_uri, get_resource_from_web, get_organisation_from_web, get_person_from_web
from SettingsResource import SettingsResource
from application_fields import application_fields, single_application_fields, repeating_application_fields, strotimer_application_fields
from auth import is_idporten_user


def parse_single_slot(data, application):
    start_time = parse_datetime(data["start_time"])
    end_time = parse_datetime(data["end_time"])
    return Slot(start_time, end_time, application)


def parse_strotime_slot(data, application):
    start_time = parse_datetime(data["start_time"])
    end_time = parse_datetime(data["end_time"])
    return StrotimeSlot(start_time, end_time, application)


def parse_repeating_slot(data, application):
    start_date = parse_date(data["start_date"])
    end_date = parse_date(data["end_date"])

    start_time = parse_time(data["start_time"])
    end_time = parse_time(data["end_time"])
    week_day = data["week_day"]
    return RepeatingSlot(
        application,
        week_day,
        start_date,
        end_date,
        start_time,
        end_time
    )


def get_period_from_slots(slots, application_type):
    period = []
    if len(slots) > 0:
        if application_type == "repeating":
            period.append(slots[0].start_date.strftime("%Y.%m.%d"))
            period.append(slots[0].end_date.strftime("%Y.%m.%d"))
    return period


def is_period_equal(period, requested_period):
    return set(period) == set(requested_period)


def is_slots_equal(slots, requested_slots):
    return set(slots) == set(requested_slots)


def render_email_template(application, status=None):
    resource_details = get_resource_from_web(application.resource.uri)
    requested_resource_details = get_resource_from_web(
        application.requested_resource.uri)
    org_name = None
    org_email = None
    org_local_email = None
    if application.organisation is not None:
        org_details = get_organisation_from_web(application.organisation.uri)
        org_name = org_details.get('name')
        org_email = org_details.get('email_address', None)
        org_local_email = org_details.get('local_email_address', None)

    email_address = None
    if application.person is not None:
        person_details = get_person_from_web(application.person.uri)
        email_address = person_details.get("email_address", None)

    resource_name = resource_details['name']
    requested_resource_name = requested_resource_details['name']
    application_time = application.application_time.strftime("%Y.%m.%d %H:%M")

    # Override status if given, used for previewing template
    if status is not None:
        application_status = format_application_status_for_email(status)
    else:
        application_status = format_application_status_for_email(
            application.status)

    application_type = application.get_type()
    requested_slots = format_slots_for_email(application.requested_slots,
                                             application_type)
    slots = format_slots_for_email(application.slots, application_type)

    requested_period = get_period_from_slots(application.requested_slots, application_type)
    period = get_period_from_slots(application.slots, application_type)

    changed_period = not is_period_equal(period, requested_period)
    changed_time = not is_slots_equal(slots, requested_slots) or changed_period

    resource_documents = resource_details.get("documents", [])

    message = render_template("email_applications_processed.txt",
                              org_name=org_name,
                              resource_name=resource_name,
                              requested_resource_name=requested_resource_name,
                              application_time=application_time,
                              message=application.message,
                              application_status=application_status,
                              resource_documents=resource_documents,
                              slots=slots,
                              requested_slots=requested_slots,
                              changed_period=changed_period,
                              changed_time=changed_time,
                              period=period,
                              requested_period=requested_period)

    return [email_address, org_email, org_local_email], message


def render_email_template_avvist_strotime(application):
    resource_details = get_resource_from_web(application.resource.uri)
    org_email = None
    org_local_email = None
    if application.organisation is not None:
        org_details = get_organisation_from_web(application.organisation.uri)
        org_email = org_details.get('email_address', None)
        org_local_email = org_details.get('local_email_address', None)

    email_address = None
    if application.person is not None:
        person_details = get_person_from_web(application.person.uri)
        email_address = person_details.get("email_address", None)

    resource_name = resource_details['name']
    application_time = application.application_time.strftime("%Y.%m.%d %H:%M")

    application_type = application.get_type()
    slots = format_slots_for_email(application.slots, application_type)

    message = render_template("email_strotime_denied.txt",
                              resource_name=resource_name,
                              application_time=application_time,
                              message=application.message,
                              slots=slots)

    return [email_address, org_email, org_local_email], message


def send_email_application_processed(application):
    email_address, message = render_email_template_avvist_strotime(application) \
        if application.type == 'strotime' and application.status == 'Denied' \
        else render_email_template(application)

    if email_address and message is not None:
        send_email_task.delay(u'Søknad om lån av lokale',
                              u'booking@trondheim.kommune.no',
                              email_address,
                              message)

    return message


def send_erv_code_mail(erv):
    erv_mail = 'apld.forsyst@evry.com'
    message = 'Se vedlagt fakturakode fra Bookingbasen Trondheim Kommune.'
    subject = 'Fakturering Bookingbasen Trondheim kommune'
    from_email = 'booking@trondheim.kommune.no'
    send_email_with_csv_task.delay(subject,
                                   from_email,
                                   [erv_mail],
                                   message,
                                   erv)


def create_ws_sak(application, resource):
    username = unsign_auth_token(request.cookies['auth_token'])
    return WSSak(resource_name=resource['name'], saksansvarlig=username)


def create_ws_journalpost(application, resource, document, ws_sak):
    person = get_person_from_web(application.person.uri)
    organisation = get_organisation_from_web(application.organisation.uri)

    adressat = WSAdressat(fornavn=person['first_name'] or '',
                          etternavn=person['last_name'] or '',
                          adresse1=person['address_line'] or '',
                          adresse2='',
                          postnr=person['postal_code'] or '',
                          sted=person['postal_city'] or '',
                          foedselsnr=person['national_identity_number'] or '',
                          orgnr=organisation['org_number'] or '')

    dok_tittel = u'Søknad godkjent: {} for lokale {}'.format(
        organisation['name'], resource['name'])
    dokument = WSDokument(dokument_tittel=dok_tittel,
                          fil_innhold=b64encode(document.encode('utf-8')))
    tittel2 = u' '.join((adressat.fornavn, adressat.etternavn))

    return WSJournalpost(adressat1=adressat,
                         saksbehandler=ws_sak['Saksansvarlig'],
                         tittel1=ws_sak['Tittel1'],
                         tittel2=tittel2,
                         dokument=dokument)


def arkiver(application, document):
    resource_details = get_resource_from_web(application.resource.uri)
    if not resource_details:
        abort(404, __error__=[u'Application resource not found'])
    arkiv_client = ArkivDBClient(current_app)

    fesak_sak = current_app.db_session.query(FesakSak).filter(
        FesakSak.application_id == application.id).first()
    if fesak_sak is None:
        ws_sak_model = create_ws_sak(application, resource_details)
        ws_sak = ws_sak_model.build()
        arkiv_client.ny_sak(application.id, ws_sak_model)
    else:
        # If fesak_sak already exists for application, use it
        # Happens when application is processed multiple times
        ws_sak = json.loads(fesak_sak.ws_sak)

    ws_journalpost = create_ws_journalpost(application, resource_details,
                                           document, ws_sak)
    arkiv_client.ny_journalpost(application.id, ws_journalpost)


def filter_applications(applications, cookies):
    """Filter applications based on user roles"""

    is_superuser = verify_superuser_auth_token(
        request.cookies.get('auth_token'))
    if is_superuser:
        # No filter for superuser
        return applications

    user = get_user(request.cookies)
    if user is None:
        abort(401)

    if has_role(user, 'flod_saksbehandlere'):
        # No filter for flod_saksbehandlere
        return applications

    if has_role(user, 'flod_brukere'):
        # Administratosr should only see applications for resources they own
        remote_resource_ids = [c['resource_id']
                               for c in user.get('credentials', [])
                               if c['id'].startswith('CAN_EDIT_FACILITY_')]

        # Need to map the ids in the credentials which uses remote ids
        # to the local ones used in booking.
        uris = ["/facilities/%s" % i for i in remote_resource_ids]
        res = current_app.db_session.query(Resource).filter(Resource.uri.in_(uris)).all()
        local_resource_ids = [r.id for r in res]

        applications = applications.filter(
            Application.resource_id.in_(local_resource_ids)
        )
    else:
        # External users should only see their own applications and the applications belonging to their organisations
        org_ids = []
        orgs = get_person_from_web('/persons/%s/organisations/' % user['person_id'])
        org_uris = [org.get('uri') for org in orgs]
        if len(org_uris) > 0:
            res = current_app.db_session.query(Organisation).filter(Organisation.uri.in_(org_uris)).all()
            org_ids = [o.id for o in res]

        person_uri = '/persons/{}'.format(user['person_id'])

        if len(org_ids) == 0:
            applications = applications.filter(
                Application.person.has(uri=person_uri)
            )
        else:
            applications = applications.filter(
                or_(
                    Application.person.has(uri=person_uri),
                    Application.organisation_id.in_(org_ids)
                )
            )

    return applications


class ApplicationResource(BaseApplicationResource):
    t = Application
    type_name = "application"

    @requires(GET, Application)
    def get(self, application_id=None):
        if application_id is not None:
            application = self.get_object_by_id(application_id)
            ensure(GET, application)

            application_dict = marshal(application, application_fields)

            # Include emails in response, if requested
            if "include_emails" in request.args:
                _, granted_message = render_email_template(application, "Granted")
                _, denied_message = render_email_template_avvist_strotime(application) if application.get_type() == 'strotime' else render_email_template(application, "Denied")
                application_dict['emails'] = dict(
                    granted_message=granted_message,
                    denied_message=denied_message
                )

            return application_dict

        applications = current_app.db_session.query(Application).order_by(Application.id)

        applications = filter_applications(applications, request.cookies)

        if "start_date" in request.args and "end_date" in request.args:
            start_date = datetime.datetime.combine(parse_date(request.args["start_date"]), datetime.datetime.min.time())
            end_date = datetime.datetime.combine(parse_date(request.args["end_date"]), datetime.datetime.max.time())

            applications = applications.filter(
                start_date <= Application.application_time,
                Application.application_time <= end_date
            )

        if "resource_uri" in request.args:
            applications = applications.filter(
                Application.resource_id == Resource.id,
                Resource.uri == request.args["resource_uri"]
            )
        if "organisation_uri" in request.args:
            applications = applications.filter(
                Application.organisation_id == Organisation.id,
                Organisation.uri == request.args["organisation_uri"]
            )
        if "status" in request.args:
            applications = applications.filter(
                Application.status == request.args["status"]
            )
        if "person_uri" in request.args:
            applications = applications.filter(
                Application.person_id == Person.id,
                Person.uri == request.args["person_uri"]
            )

        if "type" in request.args:

            if request.args["type"] == 'repeating':
                applications = applications.filter(
                    Application.requested_repeating_slots.any()
                )
            if request.args["type"] == 'single':
                applications = applications.filter(
                    Application.requested_single_slots.any()
                )
            if request.args["type"] == 'strotime':
                applications = applications.filter(
                    Application.strotime_slots.any()
                )

        return marshal(applications.all(), application_fields)

    @requires(PUT, Application)
    def put(self, application_id):
        data = request.get_json()

        application = self.get_object_by_id(application_id)
        ensure(PUT, application)

        status = data.get("status", None)
        resource_uri = data["resource"]["uri"]
        application_message = data.get("message", "")
        to_be_invoiced = data.get("to_be_invoiced", None)
        invoice_amount = data.get("invoice_amount") or None
        if invoice_amount is not None and type(invoice_amount) is not int \
                and not invoice_amount.isdigit():
            abort(400, __error__=[u'Fakturabeløp må være heltall'])
        resource = get_resource_for_uri(resource_uri)
        if not resource:
            abort(404)
        resource_details = get_resource_from_web(application.resource.uri)
        if not resource_details:
            abort(404)

        settings = SettingsResource().get()

        user = get_user(request.cookies)

        # Check that the resource allows the type of application
        if (application.get_type() == "single" and not resource.single_booking_allowed) \
                and not (application.is_arrangement and has_role(user, 'flod_saksbehandlere')):
            abort(403, __error__=[u'Det er ikke mulig å behandle en søknad om engangslån fordi type utlån er deaktivert for lokalet'])

        if application.get_type() == "repeating" and (not resource.repeating_booking_allowed
                                                      or (
                    resource.repeating_booking_allowed and not settings["repeating_booking_allowed"] and not has_role(user, 'flod_saksbehandlere'))):
            abort(403, __error__=[u'Det er ikke mulig å behandle en søknad om fast lån fordi type utlån er deaktivert for lokalet'])

        if application.get_type() == "strotime" and (not resource.auto_approval_allowed
                                                     or not settings["strotime_booking_allowed"] or not has_role(user, 'flod_saksbehandlere')):
            abort(403, __error__=[u'Det er ikke mulig å behandle en søknad om strøtimer fordi type utlån er deaktivert for lokalet'])

        # The application might have been moved to a different resource.
        application.resource = resource
        if status == "Pending":
            application.amenities = application.requested_amenities
            application.accessibility = application.requested_accessibility
            application.equipment = application.requested_equipment
            application.suitability = application.requested_suitability
            application.facilitators = application.requested_facilitators
        else:
            application.amenities = data.get('amenities')
            application.accessibility = data.get('accessibility')
            application.equipment = data.get('equipment')
            application.suitability = data.get('suitability')
            application.facilitators = data.get('facilitators')

        slot_data = data.get("slots", None)
        if status == "Granted" and not slot_data:
            abort(403, __error__=[u'Tildelt tid mangler'])

        if application.get_type() == "single":
            slots = [parse_single_slot(slot, application) for slot in slot_data]
            application.single_slots = slots
        elif application.get_type() == "repeating":
            slots = [parse_repeating_slot(slot, application) for slot in slot_data]
            application.repeating_slots = slots
        elif application.get_type() == "strotime":
            slots = [parse_strotime_slot(slot, application) for slot in slot_data]

        # Check if there are any conflicts
        for slot in slots:
            if application.get_type() == "single" or application.get_type() == "strotime":
                start_date = slot.start_time.date()
                end_date = slot.end_time.date()
                week_day = slot.start_time.isoweekday()
                start_time = slot.start_time.time()
                end_time = slot.end_time.time()
            elif application.get_type() == "repeating":
                start_date = slot.start_date
                end_date = slot.end_date
                week_day = slot.week_day
                start_time = slot.start_time
                end_time = slot.end_time

            if application.get_type() == "single":
                self.validate_end_date_of_slot(settings["single_booking_enddate"], end_date.isoformat(), u'engangslån')
            elif application.get_type() == "repeating":
                self.validate_end_date_of_slot(settings["repeating_booking_enddate"], end_date.isoformat(), u'fast lån')

            self.validate_start_and_end_times(start_date, end_date, start_time, end_time)
            if application.is_arrangement or status == "Denied":
                # NOTE: Arrangements trumph all other applications. If we reject an application, we dont nede to
                # check if the time is available...
                pass
            else:
                if self.is_conflict_slot_time(resource, start_date, end_date, week_day, start_time, end_time) or \
                        self.is_conflict_rammetid(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(
                        400,
                        __error__=[u'Tiden du har søkt på er ikke tilgjengelig']
                    )

            if status != "Denied":
                if self.is_conflict_blocked_time(resource, start_date, end_date, week_day, start_time, end_time):
                    abort(
                        400,
                        __error__=[u'Tiden du har søkt på er blokkert']
                    )

        if status == "Granted" or status == "Denied" or (status == "Pending" and len(slots) == 0):
            application.status = status
        else:
            application.status = "Processing"

        application.message = application_message
        application.invoice_amount = invoice_amount
        application.to_be_invoiced = to_be_invoiced
        application.comment = data.get('comment')

        current_app.db_session.add(application)
        current_app.db_session.commit()
        current_app.db_session.refresh(application)

        document = ''
        if status == "Granted" or status == "Denied":
            document = send_email_application_processed(application)

        # Create erv code
        if invoice_amount is not None and status == "Granted":
            invoice_amount = int(invoice_amount)
            org_number = None
            if application.organisation is not None:
                organisation = get_organisation_from_web(
                    application.organisation.uri)
                org_number = organisation.get('org_number', None)

            if org_number is None:
                person = get_person_from_web(application.person.uri)
                erv_code = erv_person(application, invoice_amount,
                                      person['national_identity_number'])
            else:
                erv_code = erv_organisation(application, invoice_amount,
                                            org_number)

            print 'erv: "{}"'.format(erv_code)
            # Skip sending mail for now
            # send_erv_code_mail("{},".format(erv_code))

        application_dict = {}
        if application.get_type() == "single":
            application_dict = marshal(application, single_application_fields)
        elif application.get_type() == "repeating":
            # Authentication is not implemented for all resources yet, so we
            # skip creating sak/journalpost if no auth_token exists
            if status == 'Granted' and 'auth_token' in request.cookies:
                arkiver(application, document)

            application_dict = marshal(application, repeating_application_fields)
        elif application.get_type() == "strotime":
            application_dict = marshal(application, strotimer_application_fields)

        # Include emails in response, if requested
        if data.get("include_emails", False):
            _, granted_message = render_email_template(application, "Granted")
            _, denied_message = render_email_template_avvist_strotime(application) if application.get_type() == 'strotime' else render_email_template(application, "Denied")
            application_dict['emails'] = dict(
                granted_message=granted_message,
                denied_message=denied_message
            )

        return application_dict

    @requires(DELETE, Application)
    def delete(self, application_id):
        application = self.get_object_by_id(application_id)
        ensure(DELETE, application)

        if is_idporten_user(get_user(request.cookies)):
            if application.status == 'Denied':
                abort(400, __error__=[u'Kan ikke slette avviste søknader'])

            if application.status == 'Granted':
                # check that no slot has started
                slots = application.slots
                for slot in slots:
                    start = slot.start_date if hasattr(slot, 'start_date') else slot.start_time.date()
                    if start <= datetime.date.today():
                        abort(400, __error__=[u'Kan ikke slette godkjente søknader når perioden er påbegynt'])

        current_app.db_session.delete(application)
        current_app.db_session.commit()
        return "", 204
