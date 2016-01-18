# -*- coding: utf-8 -*-
from collections import namedtuple
from datetime import timedelta

from flask.ext.login import UserMixin, LoginManager, current_user, login_user
from itsdangerous import URLSafeTimedSerializer

from flod_frontend import app
import os

# Login_serializer used to encryt and decrypt the cookie token for the remember me option of flask-login
from proxy import user_service_proxy, organisations_service_proxy

AUTH_ADMIN_USER_ID = 'FlodSuperUser'

app.config.update(
    SECRET_KEY=os.environ['FRONTEND_SECRET_KEY'],
    REMEMBER_COOKIE_DURATION=timedelta(days=1),
    SESSION_COOKIE_NAME="flod_session",
    REMEMBER_COOKIE_NAME="flod_remember_token"
)

login_serializer = URLSafeTimedSerializer(app.secret_key)


class AuthUser(UserMixin):
    def __init__(self, user, person=None):
        assert user
        assert getattr(user, "id", None)
        self.user_id = getattr(user, "id", None)
        self.person_id = getattr(user, "person_id", None)
        self.misc = getattr(user, "misc", None)
        if person:
            assert getattr(person, "id", None)
            self.person_id = getattr(person, "id", None)
            self.first_name = getattr(person, "first_name", None)
            self.last_name = getattr(person, "last_name", None)
            self.status = getattr(person, "status", None)
            self.phone_number = getattr(person, "phone_number", None)
            self.email_address = getattr(person, "email_address", None)

        # the id attribute is a special field used by flask-login as the key to reload the user
        data = [str(self.user_id)]
        self.id = login_serializer.dumps(data)

    def to_dict(self):
        if getattr(self, 'first_name', None) and getattr(self, 'last_name', None):
            name = self.first_name + " " + self.last_name
        else:
            name = "n/a"
        return {"person_id": self.person_id, "name": name,
                "misc": self.misc}

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


def login_user_by_private_id(private_id, idporten_parameters):
    dict_user = user_service_proxy.create_or_update_user(
        private_id
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
    auth_user = AuthUser(user, person)
    login_user(auth_user, remember=True)
    return auth_user


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


def get_current_user():
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

    return person
