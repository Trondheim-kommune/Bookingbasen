# -*- coding: utf-8 -*-

from flask import current_app, request
from flask.ext.restful import abort, marshal_with, Resource
from sqlalchemy.orm.exc import NoResultFound

from api.models import profile_fields
from domain.models import User, Profile
from validation.authentication_validators import UserIsAuthenticatedValidator
from validation.base_validators import OrValidator
from validation.request_validators import QueriedUserIdIsAuthenticatedUserValidator
from validation.role_validators import UserHasAdminRoleValidator, UserHasInternalRoleValidator


class UserProfileResource(Resource):
    @staticmethod
    def find_by_user_id(user_id):
        try:
            return current_app.db_session.query(User).filter(User.id == user_id).one().profile
        except NoResultFound:
            abort(404, __error__=["No user found for id '%s'." % user_id])

    @OrValidator(UserHasAdminRoleValidator(), QueriedUserIdIsAuthenticatedUserValidator())
    def update(self, **kwargs):
        queried_user_id = kwargs['queried_user_id']
        json_request = kwargs['json_request']
        profile = self.find_by_user_id(queried_user_id)
        if not profile:
            profile = Profile()

        if json_request.get("first_name"):
            profile.first_name = json_request.get("first_name")
        if json_request.get("last_name"):
            profile.last_name = json_request.get("last_name")
        if json_request.get("national_id_number"):
            profile.national_id_number = json_request.get("national_id_number")
        if json_request.get("email"):
            profile.email = json_request.get("email")
        if json_request.get("phone"):
            profile.phone = json_request.get("phone")

        user = current_app.db_session.query(User).filter(User.id == queried_user_id).one()
        user.profile = profile
        current_app.db_session.add(user)
        current_app.db_session.commit()
        current_app.db_session.refresh(user)
        return user.profile

    @OrValidator(UserHasAdminRoleValidator(), UserHasInternalRoleValidator(),
                 QueriedUserIdIsAuthenticatedUserValidator())
    def get_based_on_id(self, queried_user_id=None):
        return self.find_by_user_id(queried_user_id)

    @marshal_with(profile_fields)
    @UserIsAuthenticatedValidator()
    def get(self, user_id=None):
        """
        Get a user profile.

        :param user_id: ID of user
        :statuscode 200: No error
        :statuscode 400: Missing user_id parameter
        :statuscode 401: Unauthorized
        """
        if user_id:
            return self.get_based_on_id(user_id)
        else:
            abort(400, __error__=["Cannot get profile, Missing user id."])

    @marshal_with(profile_fields)
    @UserIsAuthenticatedValidator()
    def post(self, user_id=None):
        """
        Update a user profile

        :param user_id: ID of user
        :statuscode 200: No error
        :statuscode 400: Missing user_id parameter
        :statuscode 401: Unauthorized
        """
        if user_id:
            return self.update(json_request=request.get_json(), queried_user_id=user_id)
        else:
            abort(400, __error__=["Cannot post profile, missing user id."])
