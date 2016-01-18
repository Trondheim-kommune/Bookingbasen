# -*- coding: utf-8 -*-
from flask import request

from flod_common.session.utils import verify_auth_token
from validation.base_validators import ParameterizedValidator


class UserIsCookieAuthenticatedValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        valid = auth_token is not None \
            and verify_auth_token(auth_token)
        if not valid:
            self.fail("User not authenticated with cookie.",
                      f, 401, None, *args, **kwargs)
