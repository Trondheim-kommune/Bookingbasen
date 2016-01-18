# -*- coding: utf-8 -*-
from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from domain.models import User
from flod_common.session.utils import verify_auth_token
from validation.base_validators import ParameterizedValidator, OrValidator


class UserIsCookieAuthenticatedValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        auth_token = request.cookies.get('auth_token', None)
        valid = auth_token is not None \
            and verify_auth_token(auth_token)
        if not valid:
            self.fail("User not authenticated with cookie.",
                      f, 401, None, *args, **kwargs)


class UserIsAuthenticatedValidator(OrValidator):
    def __init__(self, *validators):
        super(UserIsAuthenticatedValidator, self).__init__(*validators)
        if validators and len(validators) > 0:
            raise ValueError("The " + self.__class__.__name__ + " is not supposed to receive a list of validators as "
                                                                "it builds it own.")
        self.validators = (UserIsCookieAuthenticatedValidator(),)
