# -*- coding: utf-8 -*-
from flask import request

from flod_common.session.utils import (verify_superuser_auth_token,
                                       verify_auth_token)
from validation.base_validators import ParameterizedValidator
from repo import get_user


class UserHasAdminRoleValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        valid = auth_token is not None \
                    and verify_auth_token(auth_token) and verify_superuser_auth_token(auth_token)
        if not valid:
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)


class UserRoleValidator(ParameterizedValidator):

    def __init__(self, role):
        self.role = role

    def validate(self, f, *args, **kwargs):
        user = get_user(request.cookies)
        roles = [role['name'] for role in user.get('roles', [])]
        has_role = self.role in roles
        if not has_role:
            self.fail('User is missing required role: %s' % (self.role,),
                      f, 403, None, *args, **kwargs)
