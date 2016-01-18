#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

from flask import request, abort, current_app
from flask.ext.bouncer import Bouncer, GET, PUT, POST, DELETE
from flod_common.session.utils import verify_superuser_auth_token
from repo import get_user, has_role, can_user_edit_facility
from BaseResource import get_resource_from_web, get_umbrella_organisation_from_web, get_person_from_web
from RammetidToApplication import RammetidToApplication
from domain.models import Organisation


def get_user_from_auth():
    if verify_superuser_auth_token(request.cookies.get('auth_token')):
        return {'is_superuser': True}

    user = get_user(request.cookies)
    if user is None:
        abort(401)
    return user


def if_resource_owner(resource, user):
    if not has_role(user, 'flod_brukere'):
        return False
    # Check if resource is actually a model with a resource property
    # (e.g. Application)
    if hasattr(resource, 'resource'):
        resource = resource.resource

    resource_details = get_resource_from_web(resource.uri)

    resource_id = resource_details.get('id')
    if resource_id is None:
        return False
    return can_user_edit_facility(user['id'], resource_id, request.cookies)


def is_organisation_member(organisation_id, user):
    if not is_idporten_user(user):
        return False

    if organisation_id:
        org_ids = []
        orgs = get_person_from_web('/persons/%s/organisations/' % user['person_id'])
        org_uris = [org.get('uri') for org in orgs]
        if len(org_uris) > 0:
            res = current_app.db_session.query(Organisation).filter(Organisation.uri.in_(org_uris)).all()
            org_ids = [o.id for o in res]

        return organisation_id in org_ids

    return False


def if_application_owner(application, user):
    if not is_idporten_user(user):
        return False

    person_uri = '/persons/{}'.format(user['person_id'])
    if application.person.uri == person_uri:
        return True

    is_owner = is_organisation_member(application.organisation_id, user)

    if not is_owner:
        current_app.logger.warn('User %s is not the owner: application_id=%s',
                                user, application.id)
    return is_owner


def if_slot_owner(slot, user):
    if not is_idporten_user(user):
        return False

    person_uri = '/persons/{}'.format(user['person_id'])
    if slot.application.person.uri == person_uri:
        return True

    is_slot_owner = is_organisation_member(slot.application.organisation_id, user)

    if not is_slot_owner:
        current_app.logger.warn(('User %s is not the owner of the slot: '
                                 'slot_id=%s, application_id=%s'),
                                user, slot.id, slot.application.id)
    return is_slot_owner


def is_idporten_user(user):
    return user.get('authentication_type', None) == 'id_porten'


def is_adfs_user(user):
    return user.get('authentication_type', None) == 'active_directory'


def they_can_get_applications(user, they):
    if user.get('is_superuser'):
        they.can(GET, 'Application')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(GET, 'Application')
    elif has_role(user, 'flod_brukere'):
        they.can(GET, 'Application', partial(if_resource_owner, user=user))
    elif is_idporten_user(user):
        they.can(GET, 'Application', partial(if_application_owner, user=user))


def they_can_post_applications(user, they):
    if user.get('is_superuser'):
        they.can(POST, 'Application')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(POST, 'Application')
    elif has_role(user, 'flod_brukere'):
        they.can(POST, 'Application')
    # External users
    elif is_idporten_user(user):
        they.can(POST, 'Application')


def they_can_put_applications(user, they):
    if user.get('is_superuser'):
        they.can(PUT, 'Application')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(PUT, 'Application')
    else:
        they.can(PUT, 'Application', partial(if_resource_owner, user=user))


def they_can_delete_applications(user, they):
    if user.get('is_superuser'):
        they.can(DELETE, 'Application')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(DELETE, 'Application')
    else:
        they.can(DELETE, 'Application', partial(if_application_owner, user=user))


def they_can_post_blocked_time(user, they):
    if user.get('is_superuser'):
        they.can(POST, 'BlockedTimeInterval')
        they.can(POST, 'WeeklyBlockedTime')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(POST, 'BlockedTimeInterval')
        they.can(POST, 'WeeklyBlockedTime')
    else:
        they.can(POST, 'BlockedTimeInterval', partial(if_resource_owner, user=user))
        they.can(POST, 'WeeklyBlockedTime', partial(if_resource_owner, user=user))


def they_can_delete_blocked_time(user, they):
    if user.get('is_superuser'):
        they.can(DELETE, 'BlockedTimeInterval')
        they.can(DELETE, 'WeeklyBlockedTime')
    elif has_role(user, 'flod_saksbehandlere'):
        they.can(DELETE, 'BlockedTimeInterval')
        they.can(DELETE, 'WeeklyBlockedTime')
    else:
        they.can(DELETE, 'BlockedTimeInterval', partial(if_resource_owner, user=user))
        they.can(DELETE, 'WeeklyBlockedTime', partial(if_resource_owner, user=user))


def they_can_manage_organisation_internal_notes(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_saksbehandlere'):
        they.can(GET, 'OrganisationInternalNote')
        they.can(POST, 'OrganisationInternalNote')
        they.can(DELETE, 'OrganisationInternalNote')


def is_umbrella_org_member(umbrella_org_uri, user):
    umbrella_org = get_umbrella_organisation_from_web(umbrella_org_uri)
    return any(p.get('id') == user.get('person_id') for p in umbrella_org.get('persons', []))


def if_can_post_rammetid_to_application(rammetid_to_application, user):
    return is_umbrella_org_member(rammetid_to_application.umbrella_org_uri, user)


def they_can_manage_rammetid(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_saksbehandlere'):
        they.can(POST, 'Rammetid')
        they.can(PUT, 'Rammetid')
        they.can(DELETE, 'Rammetid')

    # External users
    elif is_idporten_user(user):
        they.can(POST, RammetidToApplication, partial(if_can_post_rammetid_to_application, user=user))


def they_can_put_resources(user, they):
    if user.get('is_superuser'):
        they.can(PUT, 'Resource')

    elif has_role(user, 'flod_saksbehandlere'):
        they.can(PUT, 'Resource')

    elif has_role(user, 'flod_lokaler_admin'):
        they.can(PUT, 'Resource')

    else:
        they.can(PUT, 'Resource', partial(if_resource_owner, user=user))


def they_can_put_slots(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_saksbehandlere'):
        they.can(PUT, 'Slot')
        they.can(PUT, 'StrotimeSlot')
        they.can(PUT, 'RepeatingSlot')

    else:
        they.can(PUT, 'Slot', partial(if_slot_owner, user=user))
        they.can(PUT, 'StrotimeSlot', partial(if_slot_owner, user=user))
        they.can(PUT, 'RepeatingSlot', partial(if_slot_owner, user=user))


def they_can_delete_slots(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_saksbehandlere'):
        they.can(DELETE, 'Slot')
        they.can(DELETE, 'StrotimeSlot')
        they.can(DELETE, 'RepeatingSlot')
    else:
        they.can(DELETE, 'Slot', partial(if_slot_owner, user=user))
        they.can(DELETE, 'StrotimeSlot', partial(if_slot_owner, user=user))
        they.can(DELETE, 'RepeatingSlot', partial(if_slot_owner, user=user))


def they_can_get_statistics(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_brukere'):
        they.can(GET, 'ResourceStatistic')
        they.can(GET, 'OrganisationStatistic')
        they.can(GET, 'ExportReimbursement')
        they.can(GET, 'ExportOverview')


def they_can_manage_notifications(user, they):
    if user.get('is_superuser') or has_role(user, 'flod_saksbehandlere'):
        they.can(POST, 'ArrangementNotification')
        they.can(POST, 'StrotimeApplicationNotification')
        they.can(GET, 'ArrangementConflict')


def they_can_delete_organisations(user, they):
    if user.get('is_superuser') or has_role(user, u'flod_aktørregister_admin'):
        they.can(DELETE, 'Organisation')


def they_can_post_leieform(user, they):
    if has_role(user, 'flod_lokaler_admin'):
        they.can(POST, 'Settings')


def define_authorization(user, they):
    # Application
    they_can_get_applications(user, they)
    they_can_put_applications(user, they)
    they_can_post_applications(user, they)
    they_can_delete_applications(user, they)

    # BlockedTimeInterval and WeeklyBlockedTime
    they_can_post_blocked_time(user, they)
    they_can_delete_blocked_time(user, they)

    # OrganisationInternalNote
    they_can_manage_organisation_internal_notes(user, they)

    # Rammetid
    they_can_manage_rammetid(user, they)

    # Resource
    they_can_put_resources(user, they)

    # Slot, RepeatingSlot and StrotimeSlot
    they_can_put_slots(user, they)
    they_can_delete_slots(user, they)

    # ResourceStatistic and OrganisationStatistic, ExportReimbursement and ExportOverview
    they_can_get_statistics(user, they)

    # ArrangementConflict, ArrangementNotification and
    # StrotimeApplicationNotification
    they_can_manage_notifications(user, they)

    # Organisation
    they_can_delete_organisations(user, they)

    # Settings for leieform
    they_can_post_leieform(user, they)


def create_bouncer(app):
    bouncer = Bouncer(app)
    bouncer.get_current_user = get_user_from_auth
    bouncer._authorization_method = define_authorization
    return bouncer
