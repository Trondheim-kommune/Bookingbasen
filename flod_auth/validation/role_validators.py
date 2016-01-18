# -*- coding: utf-8 -*-
from flask import request, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from domain.models import AuthenticationTypeEnum, User
from flod_common.session.utils import (verify_auth_token, verify_superuser_auth_token,
                              unsign_auth_token)
from validation.base_validators import ParameterizedValidator, ValidationException


class UserAuthenticationTypeValidator(ParameterizedValidator):
    def verify_user_role(self, authentication_type):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is None:
            return False
        username = unsign_auth_token(auth_token)
        try:
            current_app.db_session.query(User).filter(User.id == username).filter(
                func.lower(User.authentication_type) == func.lower(authentication_type)).one()
            return True
        except NoResultFound:
            return False


class UserHasExternalRoleValidator(UserAuthenticationTypeValidator):
    def validate(self, f, *args, **kwargs):
        if not self.verify_user_role(AuthenticationTypeEnum.ID_PORTEN):
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)


class UserHasInternalRoleValidator(UserAuthenticationTypeValidator):
    def validate(self, f, *args, **kwargs):
        if not self.verify_user_role(AuthenticationTypeEnum.ACTIVE_DIRECTORY):
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)


class UserHasSpecificInternalRoleValidator(UserHasInternalRoleValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is None:
            self.fail("User is missing auth token",
                      f, 401, None, *args, **kwargs)

        username = unsign_auth_token(auth_token)
        try:
            user = current_app.db_session.query(User). \
                   filter(User.id == username). \
                   filter(func.lower(User.authentication_type) ==
                          func.lower(AuthenticationTypeEnum.ACTIVE_DIRECTORY)).one()
            for role in user.roles:
                if role.name == self.valargs[0]:
                    # User has the right role!
                    return
        except:
            # Handle unauthorized users below
            pass

        self.fail("User is not authorized to perform this action.",
                      f, 403, None, *args, **kwargs)


class UserHasAdminRoleValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        valid = auth_token is not None \
            and verify_auth_token(auth_token) and verify_superuser_auth_token(auth_token)
        if not valid:
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)
