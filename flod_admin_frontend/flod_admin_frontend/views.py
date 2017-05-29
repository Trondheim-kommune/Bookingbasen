#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import copy
import json
import os

import requests
from adfs.saml import AuthRequest, Response as IdpResponse
import calendar
from datetime import date
from datetime import datetime
from flask import (render_template, request, abort, redirect,
                   make_response, Response, flash)
from flask.ext.login import login_user, logout_user, login_required, current_user
from flod_admin_frontend import app
from flod_common.session.utils import make_auth_token

import adfs_helper
import authentication
import proxy
import repo

APP_NAME = "Bookingbasen Admin"

page_links = {
    "over":
        [
            {
                "title": u"Søknader",
                "path": "/applications"
            },
            {
                "title": u"Mine lokaler",
                "path": "/resources"
            },
            {
                "title": u"Rammetid",
                "path": "/rammetid"
            },
            {
                "title": u"Statistikk",
                "path": "/statistics"
            }
        ]
}

DEBUG = os.environ.get('DEBUG') == 'True'
DEBUG_PASSWORD = os.environ.get('DEBUG_PASSWORD')

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)


def read_config(config_file, config_path="."):
    config = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser(config_file)
    config_path = os.path.abspath(config_path)
    with open(config_path) as f:
        config.readfp(f)

    return config


@app.before_first_request
def configure_adfs():
    # Skip config if running in debug mode
    if DEBUG:
        app.logger.info('Running in debug mode, skipping ADFS configuration')
        return

    app.cfg = read_config(os.environ['FLOD_ADFS_CONFIG'])
    app.saml_settings = {
        'assertion_consumer_service_url': app.cfg.get('saml', 'assertion_consumer_service_url'),
        'issuer': app.cfg.get('saml', 'issuer'),
        'name_identifier_format': app.cfg.get('saml', 'name_identifier_format'),
        'idp_sso_target_url': app.cfg.get('saml', 'idp_sso_target_url'),
        'idp_cert_file': app.cfg.get('saml', 'idp_cert_file'),
        'sp_private_key': app.cfg.get('saml', 'secret_key'),
        'logout_target_url': app.cfg.get('saml', 'logout_target_url'),
    }

    # idp_cert_file has priority over idp_cert_fingerprint
    cert_file = app.saml_settings.pop('idp_cert_file', None)
    if cert_file:
        cert_path = os.path.expanduser(cert_file)
        cert_path = os.path.abspath(cert_path)

        with open(cert_path) as f:
            app.saml_settings['idp_cert_fingerprint'] = f.read()


def set_cookie(response, key, content):
    """Use HTTPS only cookies in non-debug mode"""
    if DEBUG:
        response.set_cookie(key, content, httponly=True)
    else:
        response.set_cookie(key, content, httponly=True, secure=True)


def login_debug():
    if request.method != 'POST':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    if DEBUG_PASSWORD is None or password != DEBUG_PASSWORD:
        app.logger.error('Running in debug mode, but DEBUG_PASSWORD is not set')
        abort(403)

    auth_user = authentication.login_user_by_private_id(username, {})
    roles = [u'flod_brukere',
             u'flod_saksbehandlere',
             u'flod_lokaler_admin',
             u'flod_aktørregister_admin']
    user_roles = authentication.update_user_roles(auth_user.user_id, roles)
    auth_user.roles = user_roles

    login_user(auth_user, remember=True)

    response = make_response(redirect(request.args.get('next') or '/'))
    set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Skip ADFS login in debug mode
    if DEBUG:
        return login_debug()

    # Default to ADFS login
    url = AuthRequest.create(**app.saml_settings)
    return redirect(url)


def get_attribute_or_404(saml_response, attribute):
    values = saml_response.get_assertion_attribute_value(attribute)
    if len(values) == 0:
        app.logger.error('Could not find attribute in SAML response: %s',
                         attribute)
        abort(404)
    return values[0]


@app.route('/adfs/ls/', methods=['POST'])
def logged_in_from_adfs():
    app.logger.info('User logged in via ADFS')
    SAMLResponse = request.values['SAMLResponse']

    try:
        res = IdpResponse(SAMLResponse, app.saml_settings["idp_cert_fingerprint"])

        res.decrypt(app.saml_settings["sp_private_key"])
        valid = res.is_valid()

        if not valid:
            app.logger.error('Invalid response from ADFS')
            abort(404)

        def to_unicode(in_str):
            return in_str.encode("utf-8")

        name_id = to_unicode(res.name_id)
        ident = get_attribute_or_404(res, "http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname")
        name = to_unicode(get_attribute_or_404(res, "http://schemas.xmlsoap.org/claims/CommonName"))
        email = to_unicode(get_attribute_or_404(res, "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"))

        app.logger.info('Logging in: name_id=%s name=%s ident=%s email=%s', name_id, name, ident, email)
        data = {"misc": {"name": name,
                         "email": email,
                         "ident": ident}}

        claims = adfs_helper.parse_claims(res._document)
        app.logger.info('Claims in SAML response: %s', claims)

        roles = adfs_helper.extract_roles(claims)
        app.logger.info('Requested roles parsed from claims: %s', roles)

        auth_user = authentication.login_user_by_private_id(ident, data)
        user_roles = authentication.update_user_roles(auth_user.user_id, roles)
        auth_user.roles = user_roles
        app.logger.info('User roles after update: %s', user_roles)

        if not auth_user.has_role('flod_brukere'):
            app.logger.info('User %s (%s) is missing required role: flod_brukere', ident, email)
            return render_template('invalid_roles.html'), 403

        app.logger.info('Logged in: %s name=%s ident=%s email=%s',
                        datetime.now().isoformat(),
                        name, ident, email)

        login_user(auth_user, remember=True)
        response = make_response(redirect(request.args.get('next') or '/'))
        set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))
        return response
    except Exception as e:
        app.logger.error('Logging failed: %s', e)
        abort(404, 'Ugyldig innlogging.')


@app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    if DEBUG:
        return redirect('/')

    # Redirect to logout path on adfs idp
    return redirect(app.saml_settings['logout_target_url'] + '?wa=wsignout1.0')


def find_facility_by_uri(uri, facilities):
    return next((facility for facility in facilities if uri == facility["uri"]),
                None)


def find_umbrella_organisation_by_uri(uri, umbrella_organisations):
    return next(umbrella_organisation for umbrella_organisation in umbrella_organisations if uri == umbrella_organisation["uri"])


def map_applications_to_facilities(applications, facilities):
    for application in applications:
        application["resource"] = find_facility_by_uri(application["resource"]["uri"], facilities)
        application["requested_resource"] = find_facility_by_uri(application["requested_resource"]["uri"], facilities)


def map_applications_to_organisations(applications, organisations):
    for application in applications:
        if "uri" in application["organisation"] and application["organisation"]["uri"]:
            organisation = next(organisation for organisation in organisations if
                                application["organisation"]["uri"] == organisation["uri"])
            application["organisation"] = organisation


def get_organisations_for_applications(applications, params):
    # get all unique organisations for all applications
    ext_org_ids = list(set([int(application["organisation"]["uri"].replace('/organisations/', '')) for application in applications if "uri" in application["organisation"] and application["organisation"]["uri"]]))
    organisations = repo.get_organisations(
        ext_org_ids,
        params,
        auth_token_username=current_user.user_id
    )
    return organisations


def map_applications_to_persons(applications, persons):
    for application in applications:
        person = next(person for person in persons if application["person"]["uri"] == person["uri"])
        application["person"] = person


def get_and_map_persons_to_applications(applications):
    # get all unique persons for all applications
    ext_person_ids = list(set([int(application['person']['uri'].replace('/persons/', '')) for application in applications]))
    persons = repo.get_persons(person_ids=ext_person_ids, auth_token_username=current_user.user_id)

    for application in applications:
        try:
            person = next(person for person in persons if person["uri"] == application["person"]["uri"])
            application["person"] = person
        except StopIteration:
            pass


def map_statistics_to_facilities(stats, facilities):
    for stat in stats:
        stat["resource"] = find_facility_by_uri(stat["resource_uri"], facilities)


def find_organisation_by_uri(uri, organisations):
    return next(organisation for organisation in organisations if uri == organisation["uri"])


def map_statistics_to_organisations(stats, organisations):
    for stat in stats:
        if stat["organisation_uri"]:
            stat["organisation"] = find_organisation_by_uri(stat["organisation_uri"], organisations)


def map_internal_notes_to_users(notes):
    for note in notes:
        note["user"] = repo.get_user(note["auth_id"], note["auth_id"])


def get_facilities_by_resources(resources, facilities):
    available_facilities = []
    for resource in resources:
        facility = find_facility_by_uri(resource["uri"], facilities)
        if facility:
            available_facilities.append(facility)
    return available_facilities


def render_flod_template(template, **kwargs):
    pages = kwargs.pop('pages', page_links)

    # Saksbehandler can add users
    is_saksbehandler = current_user.has_role('flod_saksbehandlere')
    if is_saksbehandler:
        pages = copy.deepcopy(pages)
        pages["over"].append({"title": u"Ny bruker", "path": "/new_user"})

    # Facility administrator can manage leieform for facilities
    is_admin = current_user.has_role('flod_lokaler_admin')
    if is_admin:
        pages = copy.deepcopy(pages)
        pages["over"].append({"title": u"Adm. leieform", "path": "/adm_leieform"})

    return render_template(
        template,
        pages=pages,
        app_name=APP_NAME,
        **kwargs
    )


@app.route('/')
@app.route('/applications')
@login_required
def applications():
    """Render applications page."""

    applications = None
    status = request.args.get('status', 'Pending').capitalize()
    if status not in ('Pending', 'Granted', 'Approved', 'Processing',
                      'Denied'):
        status = 'Pending'
    app_params = {'status': status}

    if status in ('Granted', 'Denied'):
        today = date.today()
        start_date = request.args.get('start_date')
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            year_ = today.year if today.month > 1 else today.year - 1
            month_ = (today.month - 1) if today.month > 1 else 12
            days_in_month = calendar.monthrange(year_, month_)[1]
            day_ = today.day if today.day <= days_in_month else days_in_month
            start_date = date(year_, month_, day_)

        end_date = request.args.get('end_date')
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = today
        app_params["start_date"] = start_date.isoformat()
        app_params["end_date"] = end_date.isoformat()

    try:
        applications = repo.get_all_applications(
            auth_token_username=current_user.user_id,
            params=app_params
        )

        # Show deleted facilities
        params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=params
        )

        # Show deleted organisations
        params = dict(show_deleted=True)
        organisations = get_organisations_for_applications(applications, params)

        map_applications_to_facilities(applications, facilities)
        map_applications_to_organisations(applications, organisations)
        get_and_map_persons_to_applications(applications)

    except Exception as e:
        app.logger.error('Proxy request failed: %s', e)
        abort(404)
    return render_flod_template(
        'applications.html',
        applications=json.dumps(applications),
        **app_params
    )


@app.route('/applications/<int:application_id>')
@login_required
def application(application_id):
    """Render application page."""
    application = None
    try:
        application = repo.get_application(
            application_id,
            auth_token_username=current_user.user_id,
            include_emails=True
        )
        params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=params
        )
        params = dict(show_deleted=True)
        organisations = repo.get_all_organisations(
            params,
            auth_token_username=current_user.user_id
        )

        arrangement_conflicts = None
        if application['is_arrangement']:
            arrangement_conflicts = repo.get_arrangement_conflicts(
                application_id,
                auth_token_username=current_user.user_id
            )
            map_applications_to_facilities(arrangement_conflicts, facilities)
            map_applications_to_organisations(arrangement_conflicts, organisations)
            get_and_map_persons_to_applications(arrangement_conflicts)

        map_applications_to_facilities([application], facilities)
        map_applications_to_organisations([application], organisations)
        get_and_map_persons_to_applications([application])

        type_mappings = json.loads(open(
            os.path.join(__location__, 'type_maps.json'),
            "r"
        ).read())

    except Exception as e:
        app.logger.error('Proxy request failed: %s', e)
        abort(404)

    return render_flod_template(
        'application.html',
        application=json.dumps(application),
        arrangement_conflicts=json.dumps(arrangement_conflicts),
        type_mappings=json.dumps(type_mappings)
    )


@app.route('/resources')
@login_required
def resource_list():
    try:
        has_facility_role = current_user.has_role('flod_lokaler_admin')
        params = dict(show_not_published=True,
                      show_only_my_facilities=not has_facility_role)

        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=params
        )
        return render_flod_template(
            'facilities_list.html',
            facilities=facilities
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/resource')
@login_required
def resource_new():
    try:
        facility_types = repo.get_all_facility_types(
            auth_token_username=current_user.user_id
        )
        unit_types = repo.get_all_unit_types(
            auth_token_username=current_user.user_id
        )

        is_facility_admin = True

        return render_flod_template(
            'facilities_detail.html',
            resources=json.dumps(None),
            facility_types=json.dumps(facility_types),
            unit_types=json.dumps(unit_types),
            is_facility_admin=json.dumps(is_facility_admin),
            auth=repo.get_user(current_user.user_id, current_user.user_id),
            notes_json=[]
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


def can_edit_facility(user_id, facility_id):
    user = repo.get_user(
        user_id,
        auth_token_username=current_user.user_id
    )

    for credential in user['credentials']:
        if credential['id'].startswith('CAN_EDIT_FACILITY') and \
                        credential['resource_id'] == str(facility_id):
            return True
    return False


@app.route('/resource/<int:facility_id>')
@login_required
def resource_detail(facility_id):
    try:
        facility_types = repo.get_all_facility_types(
            auth_token_username=current_user.user_id
        )
        unit_types = repo.get_all_unit_types(
            auth_token_username=current_user.user_id
        )
        facility = repo.get_facility(
            facility_id,
            auth_token_username=current_user.user_id
        )
        if facility.get('status') == 404:
            abort(404)

        has_facility_role = current_user.has_role('flod_lokaler_admin')
        has_edit_credentials = can_edit_facility(
            current_user.user_id,
            facility_id
        )
        is_facility_admin = has_edit_credentials or has_facility_role
        notes = repo.get_all_facilities_internal_notes(
            facility_id,
            auth_token_username=current_user.user_id
        )
        map_internal_notes_to_users(notes)

        is_saksbehandler = current_user.has_role('flod_saksbehandlere')

        return render_flod_template(
            'facilities_detail.html',
            resources=json.dumps(facility),
            facility_types=json.dumps(facility_types),
            is_facility_admin=json.dumps(is_facility_admin),
            unit_types=json.dumps(unit_types),
            auth=repo.get_user(current_user.user_id, current_user.user_id),
            is_saksbehandler=is_saksbehandler,
            notes_json=json.dumps(notes)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


statistics_page_links_under = [
    {
        "title": u"Aktør",
        "path": "/statistics/organisation"
    },
    {
        "title": u"Lokale",
        "path": "/statistics/facility"
    },
    {
        "title": u"Refusjonsgrunnlag",
        "path": "/statistics/reimbursement"
    },
    {
        "title": u"Periodeoversikt",
        "path": "/statistics/period_overview"
    }
]


@app.route('/statistics')
@login_required
def statistics():
    try:
        pages = {
            "over": page_links['over'],
            "under": statistics_page_links_under

        }

        return render_flod_template(
            'statistics.html',
            pages=pages
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/statistics/organisation')
@login_required
def organisation_statistics():
    try:
        pages = {
            "over": page_links['over'],
            "under": statistics_page_links_under
        }

        required_args = ["organisation_id", "start_date", "end_date"]

        organisations = repo.get_all_organisations(
            None,
            auth_token_username=current_user.user_id
        )

        params = {}
        for arg in required_args:
            if arg in request.args and request.args[arg]:
                params[arg] = request.args[arg]
            else:
                return render_flod_template(
                    'organisation_statistics.html',
                    organisations=organisations,
                    organisation_statistics=[],
                    params=params,
                    pages=pages
                )

        stats = repo.get_organisation_statistics(
            params['organisation_id'], display_date_to_isodate(params['start_date']), display_date_to_isodate(params['end_date']),
            auth_token_username=current_user.user_id
        )

        # Show deleted facilities
        facilities_params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=facilities_params
        )

        map_statistics_to_facilities(stats, facilities)

        total_hours = 0.0
        for stat in stats:
            total_hours += float(stat['hours'])

        return render_flod_template(
            'organisation_statistics.html',
            organisations=organisations,
            organisation_statistics=stats,
            total_hours=total_hours,
            params=params,
            pages=pages
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/statistics/facility')
@login_required
def facility_statistics():
    try:
        pages = {
            "over": page_links['over'],
            "under": statistics_page_links_under
        }

        required_args = ["facility_id", "start_date", "end_date"]

        # organisations = repo.get_all_organisations(
        #    None,
        #    auth_token_username=current_user.user_id
        #    )

        # Show deleted facilities
        facilities_params = dict(show_not_published=True)
        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=facilities_params
        )

        params = {}
        for arg in required_args:
            if arg in request.args and request.args[arg]:
                params[arg] = request.args[arg]
            else:
                return render_flod_template(
                    'facility_statistics.html',
                    facilities=facilities,
                    facility_statistics=[],
                    params=params,
                    pages=pages
                )

        stats = repo.get_facility_statistics(
            params['facility_id'], display_date_to_isodate(params['start_date']), display_date_to_isodate(params['end_date']),
            auth_token_username=current_user.user_id
        )
        params = dict(show_deleted=True)
        organisations = repo.get_all_organisations(
            params,
            auth_token_username=current_user.user_id
        )

        map_statistics_to_organisations(stats, organisations)

        total_hours = 0.0
        total_area_time = 0.0
        for stat in stats:
            total_hours += float(stat['hours'])
            total_area_time += float(stat['area_time'])

        return render_flod_template(
            'facility_statistics.html',
            facilities=facilities,
            facility_statistics=stats,
            total_hours=total_hours,
            total_area_time=total_area_time,
            params=params,
            pages=pages
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/statistics/reimbursement')
@login_required
def reimbursement_statistics():
    try:
        pages = {
            "over": page_links['over'],
            "under": statistics_page_links_under
        }

        return render_flod_template(
            'reimbursement_statistics.html',
            pages=pages
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/statistics/period_overview')
@login_required
def period_overview_statistics():
    try:
        pages = {
            "over": page_links['over'],
            "under": statistics_page_links_under
        }

        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=dict(show_not_published=True)
        )

        return render_flod_template(
            'overview_statistics.html',
            facilities=facilities,
            pages=pages
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/rammetid/')
@login_required
def rammetid_assign_time():
    try:
        umbrella_organisations = repo.get_all_umbrella_organisations(
            auth_token_username=current_user.user_id
        )
        params = {
            "booking_type": "rammetid_allowed"
        }
        resources = repo.get_resources(
            auth_token_username=current_user.user_id,
            params=params
        )
        facilities = repo.get_all_facilities(
            auth_token_username=current_user.user_id,
            params=dict(show_not_published=True)
        )
        available_resources = get_facilities_by_resources(resources, facilities)

        return render_flod_template(
            'rammetid.html',
            umbrella_organisations=json.dumps(umbrella_organisations),
            available_resources=json.dumps(available_resources),
            auth=repo.get_user(current_user.user_id, current_user.user_id))
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


def get_organisations_with_persons():
    '''
    Get a list of persons for all organisations.
    '''

    organisations = repo.get_all_organisations(
        {'include_persons': True}, auth_token_username=current_user.user_id
    )

    return organisations


def get_facilities_with_booking_type():
    '''
    A naive attempt to implement a join across two repos.
    Could probably be improved a lot with more clever backens, but seems to work
    reasonably fast...
    '''

    facilities = repo.get_all_facilities(
        auth_token_username=current_user.user_id
    )
    resources = repo.get_resources(
        {},
        auth_token_username=current_user.user_id
    )
    resources = {r['uri']: r for r in resources}
    res = []
    for facility in facilities:
        resource = resources.get("/facilities/" + str(facility['id']))
        if resource is None:
            app.logger.warn('No resource found for facility_id=%s',
                            facility['id'])
            continue

        if resource['repeating_booking_allowed']:
            facility['repeating_booking_allowed'] = True
        if resource['single_booking_allowed']:
            facility['single_booking_allowed'] = True

        res.append(facility)
    return res


@app.route('/facilities_by_booking_type/')
@login_required
def facilities_by_booking_type():
    facilities = get_facilities_with_booking_type()
    booking_type = request.args.get('type')
    if booking_type == 'single':
        facilities = filter(lambda f: f.get('single_booking_allowed', False),
                            facilities)
    elif booking_type == 'repeating':
        facilities = filter(lambda f: f.get('repeating_booking_allowed', False),
                            facilities)
    return Response(json.dumps(facilities), mimetype='application/json')


@app.route('/application_for_actor')
@login_required
def application_for_actor():
    type_mappings = json.loads(open(
        os.path.join(__location__, 'type_maps.json'),
        "r"
    ).read())

    return render_flod_template(
        'application_for_actor.html',
        facilities=json.dumps(get_facilities_with_booking_type()),
        persons=json.dumps(repo.get_all_persons(
            auth_token_username=current_user.user_id
        )),
        organisations=json.dumps(get_organisations_with_persons()),
        type_mappings=json.dumps(type_mappings)
    )


@app.route('/rammetid/<int:rammetid_id>')
@login_required
def rammetid(rammetid_id):
    rammetid = repo.get_rammetid(
        rammetid_id,
        auth_token_username=current_user.user_id
    )
    facilities = repo.get_all_facilities(
        auth_token_username=current_user.user_id,
        params=dict(show_deleted=True, show_not_published=True)
    )
    resource = find_facility_by_uri(rammetid["resource"]["uri"], facilities)

    params = dict(show_deleted=True)
    umbrella_organisations = repo.get_all_umbrella_organisations(
        auth_token_username=current_user.user_id,
        params=params
    )
    umbrella_organisation = find_umbrella_organisation_by_uri(rammetid["umbrella_organisation"]["uri"], umbrella_organisations)

    return render_flod_template(
        'rammetid/single.html',
        auth=repo.get_user(current_user.user_id, current_user.user_id),
        rammetid=json.dumps(rammetid),
        resource=resource,
        umbrella_organisation=umbrella_organisation
    )


@app.route('/adm_leieform')
@login_required
def adm_leieform():
    is_admin = current_user.has_role('flod_lokaler_admin')
    if not is_admin:
        abort(403)

    if request.method == "GET":
        return render_flod_template('adm_leieform.html')


@app.route('/new_user', methods=['GET', 'POST'])
@login_required
def new_user():
    """Render new user page page."""

    def get_form_value(key):
        if "ident" in request.form and request.form["ident"]:
            return request.form[key]
        else:
            return None

    def flash_msg(message, category):
        flash(message, category)
        return render_flod_template('new_user.html')

    def is_valid_ident(ident):
        if not ident.isupper():
            return False
        try:
            ident.decode('ascii')
            return True
        except:
            return False

    is_saksbehandler = current_user.has_role('flod_saksbehandlere')
    if not is_saksbehandler:
        abort(403)

    if request.method == "GET":
        return render_flod_template('new_user.html')

    ident = get_form_value("ident")
    if not ident:
        return flash_msg("En feil oppstod: brukernavn TK-nett mangler.",
                         "error")

    name = get_form_value("name")
    if not name:
        return flash_msg("En feil oppstod: navn mangler.", "error")

    if not is_valid_ident(ident):
        return flash_msg("En feil oppstod: brukernavn TK-nett ugyldig. Kun store bokstaver (ascii) tillatt.",
                         "error")

    users_service = proxy.gui_service_name_to_service_proxy['users']

    # Check if user already exists. Adding an
    # existing user is not allowed
    try:
        user = users_service.get_user_by_private_id(
            ident,
            auth_token_username=current_user.user_id)
        full_name = user["profile"]["full_name"]
        return flash_msg(u"Brukeren %s fantes fra før." % full_name, "error")
    except:
        app.logger.info('Saksbehandler %s adding user %s.' %
                        (current_user.user_id, ident))

    # Create user and update the (several!) profiles.
    user = users_service.create_or_update_user(
        ident,
        auth_token_username=current_user.user_id)
    data = {"misc": {"name": name, "email": "", "ident": ident}}
    user = authentication.update_profiles(user['id'], data)
    return flash_msg(u"Brukeren %s (%s) ble opprettet." % (ident, name),
                     "success")


def display_date_to_isodate(date):
    return datetime.strptime(date, '%d.%m.%Y').date()


@app.route('/release_time/repeating_application/<int:application_id>')
@login_required
def release_time_repeating_slot(application_id):
    try:
        repeating_application = repo.get_application(application_id, auth_token_username=current_user.user_id)
        # Show deleted facilities
        params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_all_facilities(auth_token_username=current_user.user_id, params=params)
        params = dict(show_deleted=True)
        organisations = repo.get_all_organisations(params, auth_token_username=current_user.user_id)
        map_applications_to_facilities([repeating_application], facilities)
        map_applications_to_organisations([repeating_application], organisations)
        get_and_map_persons_to_applications([repeating_application])
        return render_flod_template(
            'release_time_repeating_application.html',
            repeating_application=json.dumps(repeating_application)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500
