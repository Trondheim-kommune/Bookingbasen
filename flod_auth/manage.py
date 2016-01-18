# -*- coding: utf-8 -*-
import os

from flask.ext.script import Manager, Command
from app import app

from database import init_db
from domain import models
from domain.models import User, Profile, Role, Credential

manager = Manager(app)
import json

def no_map(model, mapped_models):
    return model

def map_profile(fixture, mapped_models):

    user = fixture.get("user_id", None)
    if user:
        fixture["user_id"] = mapped_models["user_models"][user]

    return fixture

def setup_db():
    app.db_session.remove()
    db_url = os.environ.get('AUTH_DATABASE_URL')
    init_db(db_url)

def add_roles(fixtures, created_models):
    role_models = {}
    for fixture in fixtures:
        role = Role(fixture.get('name'))

        role_models[role.name] = role
        app.db_session.add(role)

    created_models["role_models"] = role_models
    return created_models


def add_credentials(fixtures, created_models):
    credential_models = {}
    for fixture in fixtures:
        credential = Credential(fixture.get('id'), fixture.get('description'))
        credential.resource_id = fixture.get('resource_id')

        credential_models[credential.id] = credential
        app.db_session.add(credential)

    created_models["credential_models"] = credential_models
    return created_models


def add_users(fixtures, created_models):
    user_models = {}

    for fixture in fixtures:
        user = User(fixture.get('private_id'))
        user.db_id = fixture.get('db_id', None)
        user.id = fixture.get('id', None)
        user.authentication_type = fixture.get('authentication_type', None)
        user.person_id = fixture.get('person_id', None)
        user.created_on = fixture.get('created_on', None)
        user.auth_token = fixture.get('auth_token', None)
        user.auth_timestamp = fixture.get('auth_timestamp', None)
        user.credentials = [created_models["credential_models"][credential_id] for credential_id in fixture.get('credential_ids')]
        user.roles = [created_models["role_models"][role_name] for role_name in fixture.get('role_names')]

        profile = Profile()
        profile.national_id_number = fixture.get('profile').get('national_id_number', None)
        profile.active_directory_id = fixture.get('profile').get('active_directory_id', None)
        profile.first_name = fixture.get('profile').get('first_name', None)
        profile.last_name = fixture.get('profile').get('last_name', None)
        profile.email = fixture.get('profile').get('email', None)
        profile.phone = fixture.get('profile').get('phone', None)

        user.profile = profile

        user_models[user.db_id] = user
        app.db_session.add(user)

    created_models["user_models"] = user_models
    return created_models




@manager.command
def fixtures():
    """Install test data fixtures into the configured database."""
    print "installing fixtures.."
    setup_db()

    fixtures = json.load(open('./fixtures.json'), encoding="utf-8")

    created_models = {}

    if "credentials" in fixtures:
        add_credentials(fixtures["credentials"], created_models)

    if "profiles" in fixtures:
        add_profiles(fixtures["profiles"], created_models)

    if "roles" in fixtures:
        add_roles(fixtures["roles"], created_models)

    if "users" in fixtures:
        add_users(fixtures["users"], created_models)


    app.db_session.commit()
    print "Done!"



if __name__ == "__main__":
    manager.run()
