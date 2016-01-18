# -*- coding: utf-8 -*-
from flask import request

from flod_common.session.utils import unsign_auth_token
from validation.base_validators import ParameterizedValidator


class QueriedUserIdIsAuthenticatedUserValidator(ParameterizedValidator):
    def get_user_id_from_request(self):
        if 'auth_token' in request.cookies:
            return unsign_auth_token(request.cookies['auth_token'])
        if request.authorization:
            return request.authorization.username
        return None

    def validate(self, f, *args, **kwargs):
        queried_user_id = kwargs["queried_user_id"]
        user_id = self.get_user_id_from_request()
        valid = user_id and user_id == queried_user_id
        if not valid:
            self.fail("User is not authorized to request the resource.",
                      f, 403, None, *args, **kwargs)
