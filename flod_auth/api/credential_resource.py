# -*- coding: utf-8 -*-

from flask import current_app, request
from flask.ext.restful import abort, marshal_with, Resource
from sqlalchemy.orm.exc import NoResultFound

from flod_common.session.utils import unsign_auth_token

from api.models import credential_fields
from api.user_resource import UserResource
from domain.models import Credential
from validation.authentication_validators import UserIsAuthenticatedValidator
from validation.base_validators import OrValidator
from validation.role_validators import UserHasInternalRoleValidator, UserHasAdminRoleValidator


class CredentialResource(Resource):
    @staticmethod
    def find_all():
        return current_app.db_session.query(Credential).order_by(Credential.id.desc()).all()

    @staticmethod
    def find_by_id(user_id):
        try:
            return current_app.db_session.query(Credential).filter(Credential.id == user_id).one()
        except NoResultFound:
            abort(404, __error__=["No credential found with id %s." % user_id])

    def create(self, user_id, json_request):
        description = json_request.get("description", None)
        resource_id = json_request.get("resource_id", None)
        credential = Credential(user_id, description, resource_id)
        current_app.db_session.add(credential)
        current_app.db_session.commit()
        current_app.db_session.refresh(credential)
        return credential

    def update(self, user_id, requestJson):
        credential = self.find_by_id(user_id)
        description = requestJson.get("description", None)
        resource_id = requestJson.get("resource_id", None)
        credential.description = description
        credential.resource_id = resource_id
        current_app.db_session.add(credential)
        current_app.db_session.commit()
        current_app.db_session.refresh(credential)
        return credential

    @marshal_with(credential_fields)
    @UserIsAuthenticatedValidator()
    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator())
    def get(self, credential_id=None):
        """
        Get credentials by ID

        :param credential_id: ID of credential
        :statuscode 200: No error
        :statuscode 404: Credential does not exist
        :statuscode 401: Unauthorized
        """
        if credential_id:
            return self.find_by_id(credential_id)
        else:
            return self.find_all()

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator())
    def grant_credential_to_user(self, credential_id, user_id):
        user = UserResource.find_by_id(user_id)
        credential = self.find_by_id(credential_id)
        user.credentials.append(credential)
        current_app.db_session.add(user)
        current_app.db_session.commit()
        current_app.db_session.refresh(user)
        return credential

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator())
    def revoke_credential_from_user(self, credential_id, user_id):
        # do not allow to revoke oneself!
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is None:
            abort(400, __error__=["Missing parameters or body."])

        current_user_id = unsign_auth_token(auth_token)

        if current_user_id == user_id:
            abort(403, __error__=["Cannot revoke credentials for oneself."])

        user = UserResource.find_by_id(user_id)
        credential = self.find_by_id(credential_id)
        user.credentials.remove(credential)
        current_app.db_session.commit()
        return credential

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator())
    def create_or_update_credential(self, credential_id, json):

        try:
            current_response = None

            force_create_credential = json.get("force_create_credential", False)
            if force_create_credential:
                current_response = self.create(credential_id, json)
            else:
                try:
                    current_response = self.update(credential_id, json)
                except:
                    current_response = self.create(credential_id, json)

            user_id = json.get("user_id", None)

            if user_id:
                current_response = self.grant_credential_to_user(credential_id, user_id)

            return current_response

        except:
            current_app.db_session.rollback()
            abort(503, __error__=["A server error occured"])


    @marshal_with(credential_fields)
    @UserIsAuthenticatedValidator()
    def post(self, credential_id=None, user_id=None):
        """
        Grant a credential to an user.

        :param credential_id: ID of credential
        :param user_id: ID of user
        :statuscode 200: No error
        :statuscode 400: Missing required parameter
        :statuscode 401: Unauthorized
        """
        if credential_id:
            if user_id:
                return self.grant_credential_to_user(credential_id, user_id)
            else:
                return self.create_or_update_credential(credential_id, request.get_json())

        abort(400, __error__=["Missing parameters or body."])

    @marshal_with(credential_fields)
    @UserIsAuthenticatedValidator()
    def delete(self, credential_id=None, user_id=None):
        """
        Revoke a credential from an user.

        :param credential_id: ID of credential
        :param user_id: ID of user
        :statuscode 204: No error
        :statuscode 400: Missing required parameter
        :statuscode 401: Unauthorized
        """
        if credential_id:
            if user_id:
                self.revoke_credential_from_user(credential_id, user_id)
                return "", 204

        abort(400, __error__=["Missing parameters or body."])
