# -*- coding: utf-8 -*-

from flask import request, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

import repo
from flod_common.session.utils import (verify_superuser_auth_token,
                                       verify_auth_token,
                                       unsign_auth_token)
from validation.base_validators import ParameterizedValidator


class UserAuthenticationTypeValidator(ParameterizedValidator):

    def verify_user_role(self, role):
        auth_token = request.cookies.get('auth_token', None)
        if auth_token is None:
            return False
        username = unsign_auth_token(auth_token)

        try:
            user = repo.get_user_by_id(username, request.cookies)
            return repo.has_role(user, role)
        except Exception:
            return False


class UserHasInternalRoleValidator(UserAuthenticationTypeValidator):
    def validate(self, f, *args, **kwargs):
        if not self.verify_user_role('flod_brukere'):
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)


class UserHasOrganisationAdminRoleValidator(UserAuthenticationTypeValidator):
    def validate(self, f, *args, **kwargs):
        if not self.verify_user_role(u'flod_aktørregister_admin'):
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)


class UserHasAdminRoleValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        valid = auth_token is not None \
                    and verify_auth_token(auth_token) and verify_superuser_auth_token(auth_token)
        if not valid:
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)
