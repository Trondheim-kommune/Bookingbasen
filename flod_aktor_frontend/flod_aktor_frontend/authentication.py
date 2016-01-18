# -*- coding: utf-8 -*-
from collections import namedtuple

from datetime import timedelta
from flask.ext.login import UserMixin, LoginManager, current_user, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer
from flod_aktor_frontend import app
import os


# Login_serializer used to encryt and decrypt the cookie token for the remember me option of flask-login
from proxy import user_service_proxy, organisations_service_proxy

AUTH_ADMIN_USER_ID = 'FlodSuperUser'

app.config.update(
    SECRET_KEY=os.environ['AKTOR_FRONTEND_SECRET_KEY'],
    REMEMBER_COOKIE_DURATION=timedelta(days=1),
    SESSION_COOKIE_NAME="flod_aktor_session",
    REMEMBER_COOKIE_NAME="flod_aktor_remember_token"
)

login_serializer = URLSafeTimedSerializer(app.secret_key)

roles = [u'flod_brukere',
         u'flod_saksbehandlere',
         u'flod_lokaler_admin',
         u'flod_aktørregister_admin']
roles = {
    'adfs': {
        u'Flod brukere': u'flod_brukere',
        u'Flod saksbehandlere': u'flod_saksbehandlere',
        u'Flod lokaler-admin': u'flod_lokaler_admin',
        u'Flod aktørregister-admin': u'flod_aktørregister_admin',
        u'Tilskudd administrator': u'tilskudd_administrator',
        u'Tilskudd godkjenner': u'tilskudd_godkjenner',
        u'Tilskudd saksbehandler': u'tilskudd_saksbehandler'
    },
    'id_porten': {u'Søker': u'flod_soker'}
}


class UnAuthUser(AnonymousUserMixin):
    def userinfo(self):
        return "ANONYMOUS USER"


class AuthUser(UserMixin):
    def __init__(self, user, person=None):
        assert user
        assert getattr(user, "id", None)
        assert user.authentication_type
        self.user_id = getattr(user, "id", None)
        self.person_id = getattr(user, "person_id", None)
        self.private_id = getattr(user, 'private_id', None)
        self.misc = getattr(user, "misc", None)
        self.authentication_type = getattr(user, "authentication_type", None)

        # idporten only!
        if person:
            assert getattr(person, "id", None)
            self.person_id = getattr(person, "id", None)
            self.first_name = getattr(person, "first_name", None)
            self.last_name = getattr(person, "last_name", None)
            self.status = getattr(person, "status", None)
            self.phone_number = getattr(person, "phone_number", None)
            self.email_address = getattr(person, "email_address", None)

        # adfs only!
        print user
        self.roles = getattr(user, "roles", [])
        print self

        # the id attribute is a special field used by flask-login as the key to reload the user
        data = [str(self.user_id)]
        self.id = login_serializer.dumps(data)

    def to_dict(self):
        if getattr(self, 'first_name', None) and getattr(self, 'last_name', None):
            name = self.first_name + " " + self.last_name
        else:
            name = "n/a"
        return {
            "id": self.user_id,
            "misc": self.misc,
            "authentication_type": self.authentication_type,
            "person_id": self.person_id,
            "name": name,
            "roles": self.roles}

    def __str__(self):
        return str(self.to_dict())

    def userinfo(self):
        return str(self.user_id)

    def is_registered(self):
        return (getattr(self, 'person_id', None)
                and getattr(self, 'first_name', None)
                and getattr(self, 'last_name', None)
                and getattr(self, 'phone_number', None)
                and getattr(self, 'email_address', None)
                and getattr(self, 'status', None) == 'registered')

    def get_auth_token(self):
        data = [str(self.id)]
        return login_serializer.dumps(data)

    def has_role(self, name):
        """
        adfs only
        :param name:
        :return:
        """
        return name in (role['name'] for role in self.roles)

    def is_idporten_user(self):
        return self.authentication_type == 'id_porten'

    def is_adfs_user(self):
        return self.authentication_type == 'active_directory'

    def is_aktorregister_admin(self):
        return self.is_adfs_user() and self.has_role(u'flod_aktørregister_admin')


def login_adfs_user_by_private_id(private_id, data):
    dict_user = user_service_proxy.create_or_update_user(private_id, authentication_type='active_directory')
    if data:
        dict_user = user_service_proxy.update_user(dict_user['id'], data)
        profile_data = {'email': data['misc']['email'],
                        'last_name': data['misc']['name']}
        profile = user_service_proxy.update_user_profile(dict_user['id'], profile_data, auth_token_username=dict_user['id'])

    user_struct = namedtuple('UserStruct', ' '.join(dict_user.keys()))
    user = user_struct(**dict_user)

    # everything has been saved, we can login with flask-login
    return AuthUser(user)


def login_idporten_user_by_private_id(private_id, idporten_parameters):
    dict_user = user_service_proxy.create_or_update_user(
        private_id, authentication_type='id_porten'
    )
    dict_person = get_person_by_nin(dict_user, private_id)
    if not dict_person:
        # create person
        dict_person = organisations_service_proxy.create_person(
            private_id,
            auth_token_username=dict_user['id']
        )

    misc = {"misc": idporten_parameters}
    data = {'person_id': dict_person["id"]}
    data.update(misc)
    dict_user = user_service_proxy.update_user(
        dict_user['id'],
        data
    )

    # everything has been saved, we can login with flask-login

    user_struct = namedtuple('UserStruct', ' '.join(dict_user.keys()))
    user = user_struct(**dict_user)

    dict_person = get_person_by_nin(dict_user, private_id)

    person_struct = namedtuple('PersonStruct', ' '.join(dict_person.keys()))
    person = person_struct(**dict_person)

    return AuthUser(user, person)


def get_person_by_nin(dict_user, national_id_number):
    try:
        dict_person = organisations_service_proxy.get_person_by_national_id_number(
            national_id_number,
            auth_token_username=dict_user['id']
        )
        return dict_person
    except:
        return None


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
login_manager.anonymous_user = UnAuthUser


@login_manager.user_loader
@login_manager.token_loader
def load_user_from_token(token):
    """
        Called by flask, will obtain the authenticated auth_user as an instance of AuthUser(UserMixin).

    Attributes:
        token the serialized list containing user.id
    """
    # The Token was encrypted using itsdangerous.URLSafeTimedSerializer which
    # allows us to have a max_age on the token itself.  When the cookie is stored
    # on the users computer it also has a expiry date, but could be changed by
    # the user, so this feature allows us to enforce the expiry date of the token
    # server side and not rely on the users cookie to expire.
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    try:
        # Decrypt the Security Token, data = [username, hashpass]
        data = login_serializer.loads(token, max_age=max_age)
        user_data = user_service_proxy.get_user(
            user_id=data[0],
            auth_token_username=data[0]
        )
    except:
        return None
    if user_data:
        user_struct = namedtuple('UserStruct', ' '.join(user_data.keys()))
        return AuthUser(user_struct(**user_data))
    else:
        return None


def get_current_person():
    if current_user.authentication_type == 'id_porten':
        person = organisations_service_proxy.get_person(
            current_user.person_id,
            auth_token_username=current_user.user_id
        )

        person["person_uri"] = person["uri"]
        user = current_user.to_dict()
        person.update(user)
        person["name"] = "n/a"

        first_name = person.get("first_name", None)
        last_name = person.get("last_name", None)

        if first_name and last_name:
            person["name"] = "%s %s" % (first_name, last_name)

    else:
        person = {'person_uri': '', 'name': 'n/a'}

    return person


def update_user_roles(user_id, user_roles):
    """
    adfs only
    :param user_id:
    :param user_roles:
    :return:
    """
    user = user_service_proxy.update_user_roles(user_id, user_roles)
    return user['roles']


def adfs_roles():
    return roles['adfs']


def soker_roles():
    return roles['id_porten']
