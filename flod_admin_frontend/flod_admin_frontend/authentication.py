# -*- coding: utf-8 -*-

import os

from collections import namedtuple
from datetime import timedelta

from flask.ext.login import UserMixin, LoginManager, current_user
from itsdangerous import URLSafeTimedSerializer

from flod_admin_frontend import app


#Login_serializer used to encryt and decrypt the cookie token for the remember me option of flask-login
from proxy import user_service_proxy


app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    REMEMBER_COOKIE_DURATION=timedelta(days=1),
    SESSION_COOKIE_NAME="flod_admin_session",
    REMEMBER_COOKIE_NAME="flod_admin_remember_token"
)

login_serializer = URLSafeTimedSerializer(app.secret_key)


class AuthUser(UserMixin):
    def __init__(self, user, person=None):
        assert user.get('id') is not None
        self.user_id = user.get('id', None)
        self.person_id = user.get('person_id', None)
        self.private_id = user.get('private_id', None)
        if 'misc' in user:
            self.name = user['misc'].get('name', None)
            self.email = user['misc'].get('email', None)
        self.roles = user.get('roles', [])

        # the id attribute is a special field used by flask-login as the key to reload the user
        data = [str(self.user_id)]
        self.id = login_serializer.dumps(data)

    def to_dict(self):
        return {"person_id": self.person_id, "name": self.name}

    def get_auth_token(self):
        data = [str(self.id)]
        return login_serializer.dumps(data)

    def has_role(self, name):
        return name in (role['name'] for role in self.roles)

def update_profiles(user_id, data):
    dict_user = user_service_proxy.update_user(user_id, data)
    profile_data = {'email': data['misc']['email'],
                    'last_name': data['misc']['name']}
    profile = user_service_proxy.update_user_profile(
        dict_user["id"], profile_data, auth_token_username=dict_user["id"])
    return dict_user

def login_user_by_private_id(private_id, data):
    dict_user = user_service_proxy.create_or_update_user(private_id)
    if data:
        dict_user = update_profiles(dict_user["id"], data)

    # everything has been saved, we can login with flask-login
    return AuthUser(dict_user)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
@login_manager.token_loader
def load_user_from_token(token):
    """
        Called by flask, will obtain the authenticated auth_user as an instance of AuthUser(UserMixin).

    Attributes:
        token the serialized list containing user.id and user.auth_token
    """
    #The Token was encrypted using itsdangerous.URLSafeTimedSerializer which
    #allows us to have a max_age on the token itself.  When the cookie is stored
    #on the users computer it also has a expiry date, but could be changed by
    #the user, so this feature allows us to enforce the expiry date of the token
    #server side and not rely on the users cookie to expire.
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    try:
        #Decrypt the Security Token, data = [username, hashpass]
        data = login_serializer.loads(token, max_age=max_age)
        user_data = user_service_proxy.get_user(
            user_id=data[0],
            auth_token_username=data[0]
        )
    except:
        return None
    if user_data:
        return AuthUser(user_data)
    else:
        return None


def update_user_roles(user_id, roles):
    user = user_service_proxy.update_user_roles(user_id, roles)
    return user['roles']
