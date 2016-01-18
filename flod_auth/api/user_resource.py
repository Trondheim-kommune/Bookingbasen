# -*- coding: utf-8 -*-

from flask import current_app, request
from flask.ext.restful import abort, marshal_with, Resource
from sqlalchemy import func, asc
from sqlalchemy.orm.exc import NoResultFound

from api.models import user_fields, role_fields
from domain.models import (User, Credential, Profile, AuthenticationTypeEnum,
                           Role)
from flod_common.session.utils import unsign_auth_token
from validation.authentication_validators import UserIsCookieAuthenticatedValidator, \
    UserIsAuthenticatedValidator
from validation.base_validators import OrValidator
from validation.request_validators import QueriedUserIdIsAuthenticatedUserValidator
from validation.role_validators import UserHasAdminRoleValidator, \
    UserHasInternalRoleValidator, UserHasSpecificInternalRoleValidator


class UserResource(Resource):
    @staticmethod
    def find_by_id(user_id):
        try:
            return current_app.db_session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            abort(404, __error__=["No user found for id '%s'." % user_id])

    @staticmethod
    @UserHasAdminRoleValidator()
    def find_all():
        return current_app.db_session.query(User).order_by(asc(User.private_id)).all()

    @staticmethod
    @OrValidator(UserHasAdminRoleValidator(),
                 UserHasSpecificInternalRoleValidator("flod_saksbehandlere"))
    def find_by_private_id(private_id):
        try:
            return current_app.db_session.query(User).filter(
                func.lower(User.private_id) == func.lower(private_id)
            ).one()
        except NoResultFound:
            abort(404, __error__=["No user found for private_id '%s'." % private_id])

    @staticmethod
    def find_by_authentication_type_and_private_id_starting_with(authentication_type,
                                                                 private_id_starting_with):
        try:
            query = current_app.db_session.query(User)
            if authentication_type:
                query = query.filter(func.lower(User.authentication_type) ==
                                     func.lower(authentication_type))
            if private_id_starting_with:
                query = query.filter(func.lower(User.private_id).startswith(
                    func.lower(private_id_starting_with)))
            return query.order_by(asc(User.private_id)).all()
        except NoResultFound:
            return None

    @staticmethod
    def find_by_role(role):
        try:
            query = current_app.db_session.query(User)
            if role != None and role != "":
                query = query.filter(User.roles.any(Role.name == role))
            else:
                query = query.filter(User.roles == None)
            return query.order_by(asc(User.private_id)).all()
        except NoResultFound:
            return None

    @staticmethod
    def find_user_with_resource_credential(credential_id, resource_id):
        try:
            query = current_app.db_session.query(User).join(User.credentials)
            if credential_id:
                query = query.filter(Credential.id == credential_id)
            if resource_id:
                query = query.filter(Credential.resource_id == resource_id)
            return query.order_by(asc(User.private_id)).all()
        except NoResultFound:
            return None

    def update(self, user_id, request_json):
        user = self.find_by_id(user_id)
        if request_json.get("private_id"):
            user.private_id = request_json["private_id"]
        if request_json.get("person_id"):
            user.person_id = request_json["person_id"]
        if request_json.get("misc"):
            user.misc = request_json["misc"]
        current_app.db_session.add(user)
        current_app.db_session.commit()
        current_app.db_session.refresh(user)
        return user

    def create_or_update(self, request_json):
        private_id = request_json["private_id"]
        authentication_type = request_json["authentication_type"]
        user = None
        try:
            # update
            user = self.find_by_private_id(private_id)
            user.renew_auth()
        except:
            # create
            user = User(private_id, authentication_type=authentication_type)
            profile = Profile()
            if user.authentication_type == AuthenticationTypeEnum.ID_PORTEN:
                profile.national_id_number = private_id
            if user.authentication_type == AuthenticationTypeEnum.ACTIVE_DIRECTORY:
                profile.active_directory_id = private_id
            user.profile = profile
        current_app.db_session.add(user)
        current_app.db_session.commit()
        current_app.db_session.refresh(user)
        return user

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator(),
                 QueriedUserIdIsAuthenticatedUserValidator())
    def get_based_on_id(self, queried_user_id=None):
        return self.find_by_id(queried_user_id)

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator())
    def get_based_on_args(self):
        if "private_id" in request.args:
            return self.find_by_private_id(request.args["private_id"])
        if "authentication_type" in request.args or "private_id_starting_with" in request.args:
            authentication_type = request.args.get("authentication_type", None)
            private_id_starting_with = request.args.get("private_id_starting_with", None)
            return self.find_by_authentication_type_and_private_id_starting_with(
                authentication_type,
                private_id_starting_with)
        if "role" in request.args:
            role = request.args.get("role", None)
            return self.find_by_role(role)
        if "credential_id" in request.args or "resource_id" in request.args:
            credential_id_ = request.args.get("credential_id", None)
            resource_id_ = request.args.get("resource_id", None)
            return self.find_user_with_resource_credential(credential_id_, resource_id_)
        return self.find_all()

    def get_user_id_from_request(self):
        if 'auth_token' in request.cookies:
            return unsign_auth_token(request.cookies['auth_token'])
        if request.authorization:
            return request.authorization.username
        return None

    @marshal_with(user_fields)
    @UserIsCookieAuthenticatedValidator()
    def get(self, user_id=None):
        """
        Get an user by ID.

        :param user_id: ID of user
        :statuscode 200: No error
        :statuscode 404: User does not exist
        :statuscode 401: Unauthorized
        """
        if user_id:
            return self.get_based_on_id(queried_user_id=user_id)
        else:
            return self.get_based_on_args()

    @marshal_with(user_fields)
    @UserIsAuthenticatedValidator()
    @OrValidator(UserHasAdminRoleValidator(),
                 UserHasSpecificInternalRoleValidator("flod_saksbehandlere"))
    def post(self, user_id=None):
        """
        Create or update a user.

        :param user_id: ID of user. If omitted, a new user will be created.
        :statuscode 200: No error
        :statuscode 400: Missing required parameters
        :statuscode 401: Unauthorized
        """
        request_json = request.get_json()
        if user_id:
            return self.update(user_id, request_json)
        if request_json and request_json["private_id"]:
            return self.create_or_update(request_json)
        abort(400, __error__=["Missing parameters or payload."])


class RoleResource(Resource):

    # Mapping of external<->internal role names
    role_map = {
        u'TKA-ACC-G Flod Bruker': u'flod_brukere',
        u'TKA-ACC-G Flod-Saksbehandler': u'flod_saksbehandlere',
        u'TKA-ACC-G Flod-Lokaler-Admin': u'flod_lokaler_admin',
        u'TKA-ACC-G Flod-Aktørregister-Admin': u'flod_aktørregister_admin',
        u'TKA-ACC-G Tilskuddsbasen-Administrator': u'tilskudd_administrator',
        u'TKA-ACC-G Tilskuddsbasen-Godkjenner': u'tilskudd_godkjenner',
        u'TKA-ACC-G Tilskuddsbasen-Saksbehandler': u'tilskudd_saksbehandler'
    }

    @staticmethod
    def find_user(user_id):
        user = current_app.db_session.query(User).filter(
            User.id == user_id).first()
        if user is None:
            abort(404, __error__=['User not found'])
        return user

    @staticmethod
    def find_role(name):
        return current_app.db_session.query(Role).filter(
            Role.name == name).first()

    @staticmethod
    def create_role(name):
        role = Role(name)
        current_app.db_session.add(role)
        current_app.db_session.commit()
        return role

    @staticmethod
    def map_roles(requested_roles):
        def normalize(role_name):
            if role_name in RoleResource.role_map.values():
                return role_name
            return RoleResource.role_map.get(role_name)
        return set((r for r in map(normalize, requested_roles)
                    if r is not None))

    @marshal_with(user_fields)
    def post(self, user_id):
        """
        Set roles for a user, overwriting any existing ones.

        :param user_id: ID of user
        :statuscode 201: No error
        :statuscode 404: User does not exist
        """
        user = self.find_user(user_id)

        requested_roles = request.get_json()
        mapped_roles = self.map_roles(requested_roles)

        roles = []
        for name in mapped_roles:
            role = self.find_role(name)
            if role is None:
                role = self.create_role(name)
            roles.append(role)
        user.roles = roles

        current_app.db_session.add(user)
        current_app.db_session.commit()
        return user, 201

    @marshal_with(role_fields)
    def get(self, user_id):
        """
        Get roles for a user, overwriting any existing ones.

        :param user_id: ID of user
        :statuscode 200: No error
        :statuscode 404: User does not exist
        """
        user = self.find_user(user_id)
        return user.roles
