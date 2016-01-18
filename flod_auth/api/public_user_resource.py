# -*- coding: utf-8 -*-

from flask import current_app, request
from flask.ext.restful import abort, Resource, marshal_with

from sqlalchemy.orm.exc import NoResultFound

from api.models import public_user_fields
from domain.models import (User)
from validation.authentication_validators import UserIsCookieAuthenticatedValidator


class PublicUserResource(Resource):
    @staticmethod
    def find_by_id(user_id):
        try:
            return current_app.db_session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            abort(404, __error__=["No user found for id '%s'." % user_id])

    @staticmethod
    def find_by_ids(user_ids):
        return current_app.db_session.query(User).filter(User.id.in_(user_ids)).all()

    @marshal_with(public_user_fields)
    @UserIsCookieAuthenticatedValidator()
    def get(self, user_id=None):
        if user_id:
            return self.find_by_id(user_id)

        data = request.get_json(silent=True)
        user_ids = data.get('user_ids') if data else None
        if user_ids:
            return self.find_by_ids(user_ids)

        abort(400, __error__=["Missing parameter"])
