#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import ConfigParser

from flod_common.session.utils import ADMIN_USER_ID
import os
from datetime import date, datetime
import requests
from flask import (render_template, abort, request, redirect, Response,
                   make_response)
from flask.ext.login import logout_user, login_required, current_user
from idporten.saml import AuthRequest, LogoutRequest, Response as IdpResponse, LogoutResponse
from redirect_helper import get_redirect_target, is_safe_url
import repo
import authentication
from flod_frontend import app
from flod_common.session.utils import make_auth_token

APP_NAME = "Bookingbasen"
AKTOR_URL = os.environ.get('AKTOR_URL', 'https://aktor.trondheim.kommune.no')

page_links = {
    "over":
        [
            {
                "title": u"Forsiden",
                "path": "/"
            },
            {
                "title": u"Finn lokale",
                "path": "/search"
            },
            {
                "title": u"Mine søknader",
                "path": "/applications",
                "requires_login": True,
            },
            {
                "title": u"Om Bookingbasen",
                "path": "https://trondheim.kommune.no/lokaler/",
                "external": True
            },
            {
                "title": u"Aktørbasen",
                "path": AKTOR_URL,
                "external": True
            }
        ],
    "under":
        [
            {
                "title": u"Min profil",
                "path": "/profile",
                "right": True,
                "requires_login": True,
            }
        ]
}

DEBUG = os.environ.get('DEBUG') == 'True'


def read_config(config_file, config_path="."):
    config = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser(config_file)
    config_path = os.path.abspath(config_path)
    with open(config_path) as f:
        config.readfp(f)
    return config


app.cfg = read_config(os.environ['FLOD_SAML_CONFIG'])

settings = {
    'assertion_consumer_service_url': app.cfg.get('saml', 'assertion_consumer_service_url'),
    'issuer': app.cfg.get('saml', 'issuer'),
    'name_identifier_format': app.cfg.get('saml', 'name_identifier_format'),
    'idp_sso_target_url': app.cfg.get('saml', 'idp_sso_target_url'),
    'idp_cert_file': app.cfg.get('saml', 'idp_cert_file'),
    'private_key_file': app.cfg.get('saml', 'private_key_file'),
    'logout_target_url': app.cfg.get('saml', 'logout_target_url'),
}


@app.route('/idporten/logout_from_idp')
@login_required
def handle_logout_response():
    # Logout request from ID-porten
    if 'SAMLRequest' in request.values:
        return logout()

    saml_response = request.values['SAMLResponse']
    logout_response = LogoutResponse(saml_response)
    if not logout_response.is_success():
        app.logger.info(("Logout from Idporten failed, proceeding with logout"
                         "anyway"))

    logout_user()
    return redirect("/")


def set_cookie(response, key, content):
    """Use HTTPS only cookies in non-debug mode"""
    if DEBUG:
        response.set_cookie(key, content, httponly=True)
    else:
        response.set_cookie(key, content, httponly=True, secure=True)


@app.route('/idporten/login_from_idp', methods=['POST', "GET"])
def logged_in():
    app.logger.info("User logged in via ID-porten: request.values=%s",
                    request.values)
    SAMLResponse = request.values['SAMLResponse']

    res = IdpResponse(
        SAMLResponse,
        "TODO: remove signature parameter"
    )
    valid = res.is_valid(settings["idp_cert_file"], settings["private_key_file"])
    if valid:
        national_id_number = res.get_decrypted_assertion_attribute_value("uid")[0]
        idporten_parameters = {
            "session_index": res.get_session_index(),
            "name_id": res.name_id
        }

        auth_user = authentication.login_user_by_private_id(national_id_number,
                                                            idporten_parameters)

        # Force the user to fill in the profile if unregistered
        if not auth_user.is_registered():
            app.logger.info("Logged in: %s Uregistrert bruker (%s)",
                            datetime.now().isoformat(),
                            national_id_number[:6])
            response = make_response(redirect("/profile"))
        else:
            app.logger.info("Logged in: %s %s %s (%s)",
                            datetime.now().isoformat(),
                            auth_user.first_name,
                            auth_user.last_name,
                            national_id_number[:6])

            # Check if the user wants to redirect to a specific page
            redirect_target = request.cookies.get("redirect_target", None)
            if not redirect_target or not is_safe_url(redirect_target):
                redirect_target = None
            response = make_response(
                redirect(redirect_target or request.args.get('next') or '/'))
            # Invalidate the redirect cookie by giving it a past expiry date
            response.set_cookie("redirect_target", "", expires=0)

        set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))
        return response
    else:
        abort(404, 'Ugyldig innlogging.')


@app.route('/login_with_idporten')
def login_with_idporten():
    """Render home page."""
    auth_request = AuthRequest(**settings)
    url = auth_request.get_signed_url(settings["private_key_file"])
    app.logger.info("url=%s", url)
    return redirect(url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    response = make_response(render_template('login.html'))

    # Save the location of the page the user is trying to reach in a cookie.
    # This makes it possible to redirect correctly when user comes back
    # from id-porten.
    redirect_target = get_redirect_target()
    if redirect_target:
        set_cookie(response, "redirect_target", redirect_target)
    return response


@app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    app.logger.info("Logout requested")
    user = authentication.get_current_user()
    logout_request = LogoutRequest(name_id=user["misc"]["name_id"],
                                   session_index=user["misc"]["session_index"],
                                   **settings)
    app.logger.info("logout_request.raw_xml=%s", logout_request.raw_xml)
    url = logout_request.get_signed_url(settings["private_key_file"])
    app.logger.info("Logging out: url=%s", url)
    return redirect(url)


def render_flod_template(template, **kwargs):
    stripped_user = None
    pages = page_links
    if not current_user.is_anonymous():
        user = authentication.get_current_user()
        stripped_user = {
            "name": user['name'],
            "uri": "/persons/%d" % user['person_id']
        }

    else:
        pages = {
            'over': [link for link in page_links['over'] if not link.get('requires_login', False)],
            'under': [link for link in page_links['under'] if not link.get('requires_login', False)]
        }

    return render_template(
        template,
        user=stripped_user,
        pages=pages,
        app_name=APP_NAME,
        **kwargs
    )


### Routes ###
@app.route('/')
def home():
    """Render home page."""
    return render_flod_template(
        'home.html'
    )


@app.route('/search')
def search():
    """Render search page."""
    try:
        districts = repo.get_districts()
        facility_types = repo.get_facility_types()
        return render_flod_template(
            'search.html',
            districts=json.dumps(districts),
            facility_types=json.dumps(facility_types)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)


@app.route('/facilities/<int:facility_id>')
def facility_view(facility_id):
    """Render facility page."""

    try:

        facility = repo.get_facility(facility_id,
                                     getattr(current_user, 'user_id', None))

        # get the resource to check what kind of "rental" it allows
        resource = repo.get_resource(facility_id)
        if current_user.is_authenticated():
            organisations = repo.get_organisations_for_person(
                current_user.person_id,
                auth_token_username=current_user.user_id
            )
            allow_repeating = len(organisations) > 0  # only show repeating link to logged in user with orgs 
        else:
            allow_repeating = True  # for non-logged in user, display repeating link if resource allows it

        settings_leieform = repo.get_settings(getattr(current_user, 'user_id', None))

        facility['single_booking_allowed'] = resource['single_booking_allowed'] and settings_leieform['single_booking_allowed']
        facility['repeating_booking_allowed'] = resource['repeating_booking_allowed'] and allow_repeating and settings_leieform['repeating_booking_allowed']

        type_mappings = json.loads(open(
            os.path.join(__location__, 'type_maps.json'),
            "r"
        ).read())

        if not facility:
            abort(404, 'Could not find facility with id %s', facility_id)
            # we have to fetch the facility information
        # from backend and serve it to the template
        return render_flod_template(
            'facility.html',
            facility=facility,
            facility_json=json.dumps(facility),
            type_mappings=json.dumps(type_mappings)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/facilities/<int:facility_id>/infoscreen/')
def facility_infoscreen_view(facility_id):
    """Output booking info as json suitable for infoscreen."""

    try:
        resource = repo.get_resource(facility_id)
        if not resource or not resource.has_key("uri"):
            abort(404, 'Could not find facility with id %s' % facility_id)

        day = request.args.get("date", date.today().isoformat())
        bookings = repo.get_bookings_for_date(resource["uri"], day)
        return Response(json.dumps(bookings), mimetype='application/json')
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/booking/<int:facility_id>')
@login_required
def booking(facility_id):
    try:
        facility = repo.get_facility(facility_id, auth_token_username=current_user.user_id)

        if not facility:
            abort(404, 'Could not find facility with id %s', facility_id)

        resource = repo.get_resource(facility_id, auth_token_username=current_user.user_id)
        settings_leieform = repo.get_settings(getattr(current_user, 'user_id', None))

        if not resource['repeating_booking_allowed'] and not resource['single_booking_allowed'] and settings_leieform['single_booking_allowed']:
            return render_flod_template(
                'no_booking.html',
                message=u'Lokalet kan ikke lånes ut. Dette er fordi lokalets administator ikke har åpnet for dette.'
            )

        organisations = repo.get_organisations_for_person(
            current_user.person_id, auth_token_username=current_user.user_id)

        if not (resource['single_booking_allowed'] and settings_leieform['single_booking_allowed']) and len(organisations) == 0:
            return render_flod_template(
                'no_booking.html',
                message=u'Lokalet kan kun lånes av aktører for repeterende lån. Du tilhører ingen aktør.'
            )

        facility['single_booking_allowed'] = resource['single_booking_allowed'] and settings_leieform['single_booking_allowed']
        facility['repeating_booking_allowed'] = resource['repeating_booking_allowed'] and settings_leieform['repeating_booking_allowed'] and len(organisations) > 0

        type_mappings = json.loads(open(
            os.path.join(__location__, 'type_maps.json'),
            "r"
        ).read())

        return render_flod_template(
            'booking.html',
            facility=json.dumps(facility),
            organisations=json.dumps(organisations),
            type_mappings=json.dumps(type_mappings)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/facilities/strotime/')
@login_required
def facilities_strotime():
    """Render home page."""

    facility_type = request.args.get('facility_type', None)
    if not facility_type:
        abort(404)

    try:
        resources_with_auto_approve = repo.get_auto_approve_resources()

        if not resources_with_auto_approve:
            return Response(json.dumps([]), mimetype='application/json')

        facilities_by_type = repo.get_facilities_by_type(facility_type)
        facility_uris = [resource["uri"] for resource in resources_with_auto_approve]
        if not facilities_by_type:
            return Response(json.dumps([]), mimetype='application/json')

        facilities = [facility for facility in facilities_by_type if facility["uri"] in facility_uris]
        return Response(json.dumps(facilities), mimetype='application/json')
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/strotimer')
@login_required
def strotimer():
    """Render home page."""

    try:

        facility_types = repo.get_facility_types()
        return render_flod_template(
            'strotimer.html',
            facility_types=json.dumps(facility_types)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


def find_facility_by_uri(uri, facilities):
    return next((facility for facility in facilities if uri == facility["uri"]),
                None)


def map_applications_to_facilities(applications, facilities):
    for application in applications:
        if application["status"] == "Granted":
            application["resource"] = find_facility_by_uri(application["resource"]["uri"], facilities)
        application["requested_resource"] = find_facility_by_uri(application["requested_resource"]["uri"], facilities)


def map_organisations_to_applications(applications, organisations):
    for application in applications:
        try:
            organisation = next(organisation for organisation in organisations
                                if organisation["uri"] == application["organisation"]["uri"])
            application["organisation"] = organisation
        except StopIteration:
            pass


def get_and_map_persons_to_applications(applications):
    # get all unique persons for all applications
    ext_person_ids = list(set([int(application['person']['uri'].replace('/persons/', '')) for application in applications]))
    persons = repo.get_persons(person_ids=ext_person_ids, auth_token_username=ADMIN_USER_ID)

    for application in applications:
        try:
            person = next(person for person in persons if person["uri"] == application["person"]["uri"])
            # do not show all info about persons to id-porten users
            person_short = {
                'id': person.get('id'),
                'uri': person.get('uri'),
                'first_name': person.get('first_name'),
                'last_name': person.get('last_name'),
            }
            application["person"] = person_short
        except StopIteration:
            pass


@app.route('/applications')
@login_required
def applications():
    """Render application list page."""
    organisations = repo.get_organisations_for_person(
        current_user.person_id, auth_token_username=current_user.user_id)
    umbrella_orgs = repo.get_umbrella_organisations_for_person(current_user.person_id, auth_token_username=current_user.user_id)
    for umbrella_org in umbrella_orgs:
        umbrella_member_orgs = repo.get_umbrella_org_member_organisations(umbrella_org.get('id'), auth_token_username=current_user.user_id)
        organisations.extend(
            [umb_memb.get('organisation') for umb_memb in umbrella_member_orgs if not any(umb_memb.get('organisation').get('uri') == org.get('uri') for org in organisations)])

    try:
        applications = repo.get_applications(
            # person_uri=user["person_uri"],
            auth_token_username=current_user.user_id
        )

        # Show deleted facilities
        params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_facilities(auth_token_username=current_user.user_id, params=params)
        map_applications_to_facilities(applications, facilities)
        map_organisations_to_applications(applications, organisations)
        get_and_map_persons_to_applications(applications)
        return render_flod_template(
            'applications.html',
            applications=json.dumps(applications)
        )

    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/profile')
@login_required
def profile():
    """Render profile page."""
    user_data = authentication.get_current_user()
    try:
        organisations = repo.get_organisations_for_person(
            current_user.person_id, auth_token_username=current_user.user_id)

        umbrella_organisations = repo.get_umbrella_organisations_for_person(
            current_user.person_id,
            auth_token_username=current_user.user_id,
        )

        return render_flod_template(
            'profile.html',
            user_data=user_data,
            organisations=organisations,
            umbrella_organisations=umbrella_organisations,
            aktor_url=AKTOR_URL
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/release_time/repeating_application/<int:application_id>')
@login_required
def release_time_repeating_slot(application_id):
    organisations = repo.get_organisations_for_person(
        current_user.person_id, auth_token_username=current_user.user_id)

    umbrella_orgs = repo.get_umbrella_organisations_for_person(current_user.person_id, auth_token_username=current_user.user_id)
    for umbrella_org in umbrella_orgs:
        umbrella_member_orgs = repo.get_umbrella_org_member_organisations(umbrella_org.get('id'), auth_token_username=current_user.user_id)
        organisations.extend(
            [umb_memb.get('organisation') for umb_memb in umbrella_member_orgs if not any(umb_memb.get('organisation').get('uri') == org.get('uri') for org in organisations)])

    try:
        repeating_application = repo.get_application(
            application_id,
            auth_token_username=current_user.user_id
        )
        # Show deleted facilities
        params = dict(show_deleted=True, show_not_published=True)
        facilities = repo.get_facilities(auth_token_username=current_user.user_id, params=params)
        map_applications_to_facilities([repeating_application], facilities)
        map_organisations_to_applications([repeating_application], organisations)
        return render_flod_template(
            'release_time_repeating_application.html',
            repeating_application=json.dumps(repeating_application)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/rammetid/<int:umbrella_organisation_id>')
@login_required
def rammetid(umbrella_organisation_id):
    try:
        umbrella_organisation = repo.get_umbrella_organisation(
            umbrella_organisation_id=umbrella_organisation_id,
            auth_token_username=current_user.user_id
        )

        if umbrella_organisation.get('is_deleted', True):
            abort(404)

        if not (any(person.get('id') == current_user.person_id for person in umbrella_organisation.get('persons', []))):
            abort(404)

        member_organisations = repo.get_umbrella_org_member_organisations(
            umbrella_organisation_id=umbrella_organisation_id,
            auth_token_username=current_user.user_id
        )
        resources = repo.get_all_facilities(
            auth_token_username=current_user.user_id
        )
        return render_flod_template(
            'rammetid.html',
            umbrella_organisation=json.dumps(umbrella_organisation),
            resources=json.dumps(resources),
            member_organisations=json.dumps(member_organisations),
            umbrella_org_name=umbrella_organisation['name']
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500
