# -*- coding: utf-8 -*-

from flask import render_template

from util.email import format_slot_for_email, format_repeating_slot_for_email
from celery_tasks.email_tasks import send_email_task
from BaseResource import get_resource_from_web, get_person_from_web,\
    get_organisation_from_web

TK_EMAIL = 'booking@trondheim.kommune.no'


def get_person_name(person_data):
    if person_data['first_name'] and person_data['last_name']:
        return '%s %s' % (person_data['first_name'], person_data['last_name'])
    return None


def get_organisation_name(application):
    if application.organisation:
        organisation_data = get_organisation_from_web(
            application.organisation.uri
        )
        return organisation_data.get('name', None)
    return None


def get_organisation_emails(application):
    emails = []
    if application.organisation:
        organisation_data = get_organisation_from_web(application.organisation.uri)
        org_email = organisation_data.get('email_address')
        if org_email:
            emails.append(org_email)
        org_local_email = organisation_data.get('local_email_address')
        if org_local_email:
            emails.append(org_local_email)
    return emails


def generate_slots(application):
    if application.type == 'repeating':
        return [format_repeating_slot_for_email(slot)
                for slot in application.slots]
    else:
        return [format_slot_for_email(slot) for slot in application.slots]


def send_email_to_resource(application):
    person_data = get_person_from_web(application.person.uri)
    resource_data = get_resource_from_web(application.resource.uri)

    person_name = get_person_name(person_data)
    resource_name = resource_data.get('name', None)
    slots = generate_slots(application)

    unit_email = resource_data.get('unit_email_address', None)
    unit_name = resource_data.get('unit_name', 'Ukjent enhet')
    org_name = get_organisation_name(application)

    if application.type == 'strotime':
        to_email = unit_email
        topic = u'Strøtime tildelt'
        message = render_template(
            'email_strotime_granted_unit.txt',
            resource_name=resource_name,
            unit_name=unit_name,
            person_name=person_name,
            slots=slots
        )

    message = None
    topic = None
    to_email = None
    if application.type == 'single':
        to_email = unit_email
        topic = u'Søknad om engangslån for %s' % unit_name
        message = render_template(
            'email_single_applied_unit.txt',
            resource_name=resource_name,
            unit_name=unit_name,
            person_name=person_name,
            slots=slots,
            organisation_name=org_name
        )

    if application.type == 'repeating':
        to_email = TK_EMAIL
        topic = u'Søknad om fast lån for %s' % unit_name
        message = render_template(
            'email_repeating_applied_unit.txt',
            resource_name=resource_name,
            unit_name=unit_name,
            person_name=person_name,
            slots=slots,
            organisation_name=org_name
        )

    if not to_email or not topic or not message:
        return

    send_email_task.delay(
        topic,
        u'booking@trondheim.kommune.no',
        [to_email],
        message
    )


def send_email_to_applicant(application):
    person_data = get_person_from_web(application.person.uri)
    resource_data = get_resource_from_web(application.resource.uri)

    person_email = person_data.get('email_address')
    resource_name = resource_data.get('name', None)

    message = None
    topic = None
    reciepients = []
    if person_email:
        reciepients.append(person_email)

    if application.type == 'single':
        topic = u'Søknad om engangslån mottatt'
        message = render_template(
            'email_single_application_created.txt',
            resource_name=resource_name
        )

    if application.type == 'repeating':
        topic = u'Søknad om fastlån mottatt'
        reciepients.extend(get_organisation_emails(application))
        message = render_template(
            'email_repeating_application_created.txt',
            resource_name=resource_name
        )

    if not reciepients or not topic or not message:
        return

    send_email_task.delay(
        topic,
        u'booking@trondheim.kommune.no',
        reciepients,
        message
    )
