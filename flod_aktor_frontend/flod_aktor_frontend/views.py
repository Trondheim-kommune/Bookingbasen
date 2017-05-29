#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import ConfigParser

from flod_common.session.cookie_helper import get_auth_type_from_cookie, get_redirect_target_from_cookie, invalidate_redirect_target_cookie, set_auth_type_cookie, \
    set_redirect_target_cookie
import os
from datetime import datetime
import requests
from flask import (render_template, abort, request, redirect, make_response)
from flask.ext.login import login_user, \
    logout_user, login_required, current_user
from idporten.saml import AuthRequest, LogoutRequest, Response as IdpResponse, LogoutResponse
import repo
import authentication
from adfs.saml import AuthRequest as ADFSAuthRequest, Response as ADFSResponse
from flod_aktor_frontend import app
import proxy
import adfs_helper
from flod_common.session.utils import make_auth_token
import xmlParser

APP_NAME = u"Aktørbasen"


@app.errorhandler(401)
def not_authorized_handler(e):
    return 'Ingen tilgang til siden', 401


def page_links():
    over = [
        {
            "title": u"Forsiden",
            "path": "/"
        },
        {
            "title": u"Finn aktør",
            "path": "/organisations"
        }
    ]

    under = []

    if not current_user.is_authenticated() or current_user.is_idporten_user() or current_user.is_aktorregister_admin():
        over.append({
            "title": u"Registrer aktør",
            "path": "/register_org"
        })

    if current_user.is_authenticated():
        if current_user.is_aktorregister_admin():
            over.append({
                "title": u"Oppdater medlemsdata",
                "path": "/organisations/updatememberdata"
            })
            over.append({
                "title": u"Paraplyorganisasjoner",
                "path": "/umbrella_organisations"
            })

        if current_user.is_idporten_user():
            under.append(
                {
                    "title": u"Min profil",
                    "path": "/profile",
                    "right": True,
                    "requires_login": True,
                }
            )

    over.append({
        "title": u"Om Aktørbasen",
        "path": "https://www.trondheim.kommune.no/aktorbasen/",
        "external": True
    })

    links = {
        "over": over,
        "under": under
    }

    return links


DEBUG = os.environ.get('DEBUG') == 'True'
DEBUG_PASSWORD = os.environ.get('DEBUG_PASSWORD')

# specifically mock idporten and adfs if set. remove from prod?
MOCK_IDPORTEN = os.environ.get('MOCK_IDPORTEN') == 'True'
MOCK_ADFS = os.environ.get('MOCK_ADFS') == 'True'


def read_config(config_file, config_path="."):
    config = ConfigParser.RawConfigParser()
    config_path = os.path.expanduser(config_file)
    config_path = os.path.abspath(config_path)
    with open(config_path) as f:
        config.readfp(f)
    return config


@app.before_first_request
def configure_idporten():
    # skip config if mocking
    if MOCK_IDPORTEN:
        app.logger.info("Running in test/dev environment with mocked IDPorten. Skip IDPorten configuration.")
        return

    app.idporten_config = read_config(os.environ['FLOD_AKTOR_SAML_CONFIG'])

    # IDporten settings
    app.idporten_settings = {
        'assertion_consumer_service_url': app.idporten_config.get('saml', 'assertion_consumer_service_url'),
        'issuer': app.idporten_config.get('saml', 'issuer'),
        'name_identifier_format': app.idporten_config.get('saml', 'name_identifier_format'),
        'idp_sso_target_url': app.idporten_config.get('saml', 'idp_sso_target_url'),
        'idp_cert_file': app.idporten_config.get('saml', 'idp_cert_file'),
        'private_key_file': app.idporten_config.get('saml', 'private_key_file'),
        'logout_target_url': app.idporten_config.get('saml', 'logout_target_url'),
    }


@app.before_first_request
def configure_adfs():
    # Skip config if mocking
    if MOCK_ADFS:
        app.logger.info('Running in test/dev environment with mocked ADFS. Skip ADFS configuration.')
        return

    app.adfs_config = read_config(os.environ['FLOD_AKTOR_ADFS_CONFIG'])
    app.adfs_settings = {
        'assertion_consumer_service_url': app.adfs_config.get('saml', 'assertion_consumer_service_url'),
        'issuer': app.adfs_config.get('saml', 'issuer'),
        'name_identifier_format': app.adfs_config.get('saml', 'name_identifier_format'),
        'idp_sso_target_url': app.adfs_config.get('saml', 'idp_sso_target_url'),
        'idp_cert_file': app.adfs_config.get('saml', 'idp_cert_file'),
        'sp_private_key': app.adfs_config.get('saml', 'secret_key'),
        'logout_target_url': app.adfs_config.get('saml', 'logout_target_url'),
    }

    # idp_cert_file has priority over idp_cert_fingerprint
    cert_file = app.adfs_settings.pop('idp_cert_file', None)
    if cert_file:
        cert_path = os.path.expanduser(cert_file)
        cert_path = os.path.abspath(cert_path)

        with open(cert_path) as f:
            app.adfs_settings['idp_cert_fingerprint'] = f.read()


def get_attribute_or_404(saml_response, attribute):
    values = saml_response.get_assertion_attribute_value(attribute)
    if len(values) == 0:
        app.logger.error('Could not find attribute in SAML response: %s',
                         attribute)
        abort(404)
    return values[0]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        response = redirect(request.args.get('next') or '/')

    else:
        auth_type = get_auth_type_from_cookie(request)

        if auth_type == 'active_directory':
            response = redirect('/admin/login')
        else:
            response = make_response(render_template('login.html', app_name=APP_NAME))

        # Save the location of the page the user is trying to reach in a cookie.
        # This makes it possible to redirect correctly when user comes back
        # from id-porten/adfs.
        set_redirect_target_cookie(response)

    return response


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Skip ADFS login in when mocking
    if MOCK_ADFS:
        return login_adfs_mock()

    # Default to ADFS login
    url = ADFSAuthRequest.create(**app.adfs_settings)
    return redirect(url)


@app.route('/adfs/ls/', methods=['POST'])
def logged_in_from_adfs():
    app.logger.info('User logged in via ADFS')
    SAMLResponse = request.values['SAMLResponse']

    try:
        res = ADFSResponse(SAMLResponse, app.adfs_settings["idp_cert_fingerprint"])

        res.decrypt(app.adfs_settings["sp_private_key"])
        valid = res.is_valid()

        if not valid:
            app.logger.error('Invalid response from ADFS')
            abort(404)

        def to_unicode(in_str):
            return in_str.encode("utf-8")

        name_id = to_unicode(res.name_id)
        ident = get_attribute_or_404(res, "http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname")
        name = to_unicode(get_attribute_or_404(res, "http://schemas.xmlsoap.org/claims/CommonName"))
        email = to_unicode(
            get_attribute_or_404(res, "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"))

        app.logger.info('Logging in: name_id=%s name=%s ident=%s email=%s', name_id, name, ident, email)
        data = {"misc": {"name": name,
                         "email": email,
                         "ident": ident}}

        claims = adfs_helper.parse_claims(res._document)
        app.logger.info('Claims in SAML response: %s', claims)

        roles = adfs_helper.extract_roles(claims)
        app.logger.info('Requested roles parsed from claims: %s', roles)

        auth_user = authentication.login_adfs_user_by_private_id(ident, data)
        user_roles = authentication.update_user_roles(auth_user.user_id, roles)
        auth_user.roles = user_roles
        app.logger.info('User roles after update: %s', user_roles)

        app.logger.info('Logged in: %s name=%s ident=%s email=%s',
                        datetime.now().isoformat(),
                        name, ident, email)

        login_user(auth_user, remember=True)
        # Check if the user wants to redirect to a specific page
        redirect_target = get_redirect_target_from_cookie(request)
        response = make_response(redirect(redirect_target or request.args.get('next') or '/'))
        invalidate_redirect_target_cookie(response)

        set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))

        # set authentication type cookie
        set_auth_type_cookie(response, "active_directory")

        return response
    except Exception as e:
        app.logger.error('Logging failed: %s', e)
        abort(404, 'Ugyldig innlogging.')


def login_adfs_mock():
    if request.method != 'POST':
        return render_template('admin_login.html', roles=authentication.adfs_roles())

    username = request.form['username']
    password = request.form['password']
    if DEBUG_PASSWORD is None or password != DEBUG_PASSWORD:
        app.logger.error('Running in debug mode, but DEBUG_PASSWORD is not set')
        abort(403)

    auth_user = authentication.login_adfs_user_by_private_id(username, {})

    roles = request.form.getlist('roles')
    user_roles = authentication.update_user_roles(auth_user.user_id, roles)
    auth_user.roles = user_roles

    login_user(auth_user, remember=True)
    # Check if the user wants to redirect to a specific page
    redirect_target = get_redirect_target_from_cookie(request)
    response = make_response(redirect(redirect_target or request.args.get('next') or '/'))
    invalidate_redirect_target_cookie(response)

    set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))

    # set authentication type cookie
    set_auth_type_cookie(response, "active_directory")

    return response


@app.route('/bruker/login', methods=['GET', 'POST'])
def bruker_login():
    if MOCK_IDPORTEN:
        return login_idporten_mock()

    # Encrypt "authentication" URL with our private key. We redirect to that URL.
    auth_request = AuthRequest(**app.idporten_settings)
    url = auth_request.get_signed_url(app.idporten_settings["private_key_file"])
    app.logger.info("url=%s", url)
    return redirect(url)


@app.route('/idporten/login_from_idp', methods=['POST', 'GET'])
def logged_in():
    # IDPorten redirects to this URL if all ok with login
    app.logger.info("User logged in via ID-porten: request.values=%s",
                    request.values)
    SAMLResponse = request.values['SAMLResponse']

    res = IdpResponse(
        SAMLResponse,
        "TODO: remove signature parameter"
    )

    # Decrypt response from IDPorten with our private key, and make sure that the response is valid
    # (it was encrypted with same key)
    valid = res.is_valid(app.idporten_settings["idp_cert_file"], app.idporten_settings["private_key_file"])
    if valid:
        national_id_number = res.get_decrypted_assertion_attribute_value("uid")[0]
        idporten_parameters = {
            "session_index": res.get_session_index(),
            "name_id": res.name_id
        }

        auth_user = authentication.login_idporten_user_by_private_id(national_id_number,
                                                                     idporten_parameters)
        login_user(auth_user, remember=True)

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
            redirect_target = get_redirect_target_from_cookie(request)
            response = make_response(redirect(redirect_target or request.args.get('next') or '/'))
            invalidate_redirect_target_cookie(response)

        set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))
        return response
    else:
        abort(404, 'Ugyldig innlogging.')


def login_idporten_mock():
    if request.method != 'POST':
        return render_template('bruker_login.html')

    ssn = request.form['ssn']
    password = request.form['password']
    if DEBUG_PASSWORD is None or password != DEBUG_PASSWORD:
        app.logger.error('Running in debug mode, incorrect DEBUG_PASSWORD or not set')
        abort(403)

    auth_user = authentication.login_idporten_user_by_private_id(ssn, {})
    login_user(auth_user, remember=True)

    # Force the user to fill in the profile if unregistered
    if not auth_user.is_registered():
        response = make_response(redirect("/profil"))
    else:
        # Check if the user wants to redirect to a specific page
        redirect_target = get_redirect_target_from_cookie(request)
        response = make_response(redirect(redirect_target or request.args.get('next') or '/'))
        invalidate_redirect_target_cookie(response)

    set_cookie(response, 'auth_token', make_auth_token(auth_user.user_id))

    return response


@app.route('/logout')
def logout():
    # Remove the user information from the session
    app.logger.info("Logout requested")

    url = '/'

    if current_user.authentication_type == 'id_porten':

        if MOCK_IDPORTEN:
            logout_user()
            return redirect('/')

        logout_request = LogoutRequest(name_id=current_user.misc["name_id"],
                                       session_index=current_user.misc["session_index"],
                                       **app.idporten_settings)
        app.logger.info("logout_request.raw_xml=%s", logout_request.raw_xml)
        url = logout_request.get_signed_url(app.idporten_settings["private_key_file"])
        app.logger.info("Logging out: url=%s", url)

    elif current_user.authentication_type == 'active_directory':

        if MOCK_ADFS:
            logout_user()
            return redirect('/')

        # Note: We never really log out from adfs, it is SSO in TK and we only want
        # to log out from our system
        logout_user()

        # Redirect to logout path on adfs idp
        url = app.adfs_settings['logout_target_url'] + '?wa=wsignout1.0'
        app.logger.info("Logging out: url=%s", url)

    return redirect(url)


@app.route('/idporten/logout_from_idp')
def handle_idporten_logout_response():
    # If user logs out IN IDporten, then IDporten sends the logout request to us
    # , and we need to continue the logout process the normal way
    if 'SAMLRequest' in request.values:
        return logout()

    # Got response from logout request from IDporten, continue logging out
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


def render_flod_template(template, **kwargs):
    stripped_user = None
    stripped_person = None

    user_mode = None

    if not current_user.is_anonymous():

        if current_user.is_idporten_user():
            person = authentication.get_current_person()
            stripped_person = {
                "name": person['name'],
                "uri": "/persons/%d" % person['person_id'],
                "id": person['person_id']
            }
            user_mode = 'soker'
        elif current_user.is_adfs_user() and current_user.is_aktorregister_admin():
            user_mode = 'admin'

        stripped_user = {
            "id": current_user.user_id,
            "private_id": current_user.private_id
        }

    return render_template(
        template,
        person=stripped_person,
        user=stripped_user,
        pages=page_links(),
        app_name=APP_NAME,
        user_mode=user_mode,
        **kwargs
    )


### Routes ###
@app.route('/')
def home():
    """Render home page."""
    return render_flod_template(
        'home.html',
        can_register=not current_user.is_authenticated() or current_user.is_idporten_user() or current_user.is_aktorregister_admin()
    )


@app.route('/profile')
@login_required
def profile():
    """Render profile page."""
    user_data = authentication.get_current_person()
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
            umbrella_organisations=umbrella_organisations
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/organisations')
def organisations_list():
    allowed_args = ["name", "brreg_activity_code", "flod_activity_type", "area"]

    params = {}
    for arg in allowed_args:
        if arg in request.args and request.args[arg]:
            params[arg] = request.args[arg]

    try:
        flod_activity_types = repo.get_flod_activity_types()
        brreg_activity_codes = repo.get_brreg_activity_codes()
        districts = repo.get_districts_without_whole_trd()

        if params:
            if current_user.is_anonymous():
                user_id = None
            else:
                user_id = current_user.user_id

            organisations = repo.get_all_organisations(params, user_id)
        else:
            organisations = []

        emails = []
        if current_user.is_authenticated() and current_user.is_aktorregister_admin():
            emails = [email for email in (o.get('email_address') for o in organisations) if email]
            emails += [email for email in (o.get('local_email_address') for o in organisations) if email]

        return render_flod_template(
            'organisations_list.html',
            organisations=organisations,
            params=params,
            emails=json.dumps(emails),
            brreg_activity_codes=brreg_activity_codes,
            flod_activity_types=flod_activity_types,
            districts=districts
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/register_org')
@login_required
def register_org():
    if not (current_user.is_idporten_user() or current_user.is_aktorregister_admin()):
        abort(401)

    """Render home page."""
    try:
        recruiting_districts = repo.get_districts()
        districts = repo.get_districts_without_whole_trd()

        brreg_activity_codes = repo.get_brreg_activity_codes()

        return render_flod_template(
            'register_org.html',
            districts=json.dumps(districts),
            recruiting_districts=json.dumps(recruiting_districts),
            brreg_activity_codes=json.dumps(brreg_activity_codes)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


def render_org_template(template, organisation_id, requires_owner=True, **kwargs):
    try:
        is_member = True
        if current_user.is_authenticated() and current_user.is_idporten_user():
            organisations = repo.get_organisations_for_person(
                current_user.person_id,
                auth_token_username=current_user.user_id)
            try:
                org = next(org for org in organisations if org["id"] == organisation_id)
                is_member = True
            except StopIteration:
                if requires_owner:
                    abort(403)
                is_member = False

        return render_flod_template(
            template,
            organisation_id=organisation_id,
            is_member=is_member,
            **kwargs
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route("/organisations/<int:organisation_id>")
def organisation(organisation_id):
    try:

        organisation = repo.get_organisation(
            organisation_id, getattr(current_user, 'user_id', None))

        recruiting_districts = repo.get_districts()
        districts = repo.get_districts_without_whole_trd()

        try:
            organisation["area"] = next(
                district["name"] for district in districts if district["id"] == organisation.get("area"))
        except StopIteration:
            organisation["area"] = None

        try:
            organisation["recruitment_area"] = next(
                district["name"] for district in recruiting_districts if district["id"] == organisation.get("recruitment_area"))
        except StopIteration:
            organisation["recruitment_area"] = None

        brreg_activity_codes = repo.get_brreg_activity_codes()

        organisation["brreg_activity_code"] = [code for code in brreg_activity_codes if
                                               code["code"] in organisation.get("brreg_activity_code", [])]

        activity_types = [type["flod_activity_types"] for type in organisation.get("brreg_activity_code")]
        activity_types = [y for x in activity_types for y in x]

        organisation["flod_activity_type"] = [type for type in activity_types if
                                              type["id"] in organisation.get("flod_activity_type", [])]

        for key, value in organisation.items():
            if value == "" or value is None:
                del organisation[key]

        return render_org_template(
            'org_info.html',
            organisation_id,
            requires_owner=False,
            organisation=organisation
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500
    except requests.exceptions.HTTPError as e:
        abort(e.response.status_code)


@app.route("/organisations/<int:organisation_id>/edit")
@login_required
def edit_organisation(organisation_id):
    try:
        recruiting_districts = repo.get_districts()
        districts = repo.get_districts_without_whole_trd()
        brreg_activity_codes = repo.get_brreg_activity_codes()

        organisation = repo.get_organisation(
            organisation_id, getattr(current_user, 'user_id', None))

        return render_org_template(
            'edit_org.html',
            organisation_id,
            organisation=json.dumps(organisation),
            districts=json.dumps(districts),
            recruiting_districts=json.dumps(recruiting_districts),
            brreg_activity_codes=json.dumps(brreg_activity_codes)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500
    except requests.exceptions.HTTPError as e:
        abort(e.response.status_code)


@app.route("/organisations/<int:organisation_id>/members")
@login_required
def add_org_members(organisation_id):
    try:
        organisation = repo.get_organisation(
            organisation_id, getattr(current_user, 'user_id', None))

        members = repo.get_members(
            organisation_id,
            auth_token_username=current_user.user_id
        )

        return render_org_template(
            'org_members.html',
            organisation_id,
            organisation=organisation,
            members=json.dumps(members)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


def map_internal_notes_to_users(notes):
    for note in notes:
        note["user"] = repo.get_user(note["auth_id"], note["auth_id"])


@app.route("/organisations/<int:organisation_id>/internal_notes")
@login_required
def internal_notes(organisation_id):
    try:
        organisation = repo.get_organisation(
            organisation_id, getattr(current_user, 'user_id', None))

        notes = repo.get_notes(organisation_id, getattr(current_user, 'user_id', None))
        map_internal_notes_to_users(notes)

        return render_org_template(
            'internal_notes.html',
            organisation_id,
            organisation=json.dumps(organisation),
            internal_notes=json.dumps(notes)
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
    return "", 500


@app.route('/organisations/updatememberdata', methods=['GET', 'POST'])
@login_required
def organisation_update_member_data():
    if not (current_user.is_authenticated() and current_user.is_aktorregister_admin()):
        abort(401)

    try:
        # Not ideal, we should have a fixed setting
        # Will cause 413 if exceeded
        app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

        allowed_extensions = ['xml']
        messages = []
        updated_organisations = []

        if request.method == 'POST' and len(request.files) > 0:
            file = request.files['document']
            filename = file.filename
            if '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions:
                organisations = xmlParser.get_organisations_from_nif_idrettsraad_xml(file.stream)
                organisations_service = proxy.gui_service_name_to_service_proxy['organisations']
                updated_organisations = organisations_service.update_organisations(organisations, auth_token_username=current_user.user_id)
                messages.append({'status': 'success', 'message': 'Filen ble parset. Se under for hvilke organisasjoner som ble oppdatert.'})
            else:
                messages.append({'status': 'error', 'message': u'Ugyldig filtype. Filnavnet må være på formatet "filnavn.xml"'})

        return render_flod_template(
            'organisations_updatemembers.html',
            messages=messages,
            updated_organisations=updated_organisations
        )

    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/umbrella_organisations')
@login_required
def umbrella_organisations_list():
    if not (current_user.is_authenticated() and current_user.is_aktorregister_admin()):
        abort(401)

    try:
        umbrella_organisations = repo.get_all_umbrella_organisations(
            auth_token_username=current_user.user_id
        )

        return render_flod_template(
            'umbrella_organisations_list.html',
            umbrella_organisations=umbrella_organisations
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/umbrella_organisation/<int:id>')
@login_required
def umbrella_organisation_detail(id):
    if not (current_user.is_authenticated() and current_user.is_aktorregister_admin()):
        abort(401)

    try:
        umbrella_organisation = repo.get_umbrella_organisation(
            id,
            auth_token_username=current_user.user_id
        )

        flod_activity_types = repo.get_flod_activity_types()
        brreg_activity_codes = repo.get_brreg_activity_codes()

        return render_flod_template(
            'umbrella_organisation_detail.html',
            umbrella_organisation=json.dumps(umbrella_organisation),
            auth=repo.get_user(current_user.user_id, current_user.user_id),
            brreg_activity_codes=brreg_activity_codes,
            flod_activity_types=flod_activity_types
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500


@app.route('/umbrella_organisation')
@login_required
def umbrella_organisation_new():
    if not (current_user.is_authenticated() and current_user.is_aktorregister_admin()):
        abort(401)

    flod_activity_types = repo.get_flod_activity_types()
    brreg_activity_codes = repo.get_brreg_activity_codes()

    try:
        return render_flod_template(
            'umbrella_organisation_detail.html',
            umbrella_organisation=json.dumps(None),
            auth=repo.get_user(current_user.user_id, current_user.user_id),
            brreg_activity_codes=brreg_activity_codes,
            flod_activity_types=flod_activity_types
        )
    except requests.exceptions.ConnectionError:
        app.logger.exception('Request failed')
        return "", 500
