# -*- coding: utf-8 -*-
from flask.ext.restful import fields

from api.ISO8601DateTime import ISO8601DateTime


class FullNameString(fields.Raw):
    def format(self, value):
        return value()

credential_fields = {
    'id': fields.String(default=None),
    'uri': fields.String(default=None),
    'description': fields.String(default=None),
    'resource_id': fields.String(default=None)
}

profile_fields = {
    'first_name': fields.String(default=None),
    'last_name': fields.String(default=None),
    'full_name' : FullNameString(default=None),
    'national_id_number': fields.String(default=None),
    'email': fields.String(default=None),
    'phone': fields.Integer(default=None)
}

public_profile_fields = {
    'first_name': fields.String(default=None),
    'last_name': fields.String(default=None),
    'full_name' : FullNameString(default=None),
    'email': fields.String(default=None),
    'phone': fields.Integer(default=None)
}

role_fields = {
    'id': fields.Integer(),
    'name': fields.String()
}

user_fields = {
    'id': fields.String(default=None),
    'authentication_type': fields.String(default=None),
    'person_id': fields.Integer(default=None),
    'private_id': fields.String(default=None),
    'created_on': ISO8601DateTime(default=None),
    'auth_timestamp': ISO8601DateTime(default=None),
    'profile': fields.Nested(profile_fields, default=None),
    'credentials': fields.Nested(credential_fields, default=None),
    'misc': fields.Raw(default={}),
    'roles': fields.Nested(role_fields, default=[])
}

public_user_fields = {
    'id': fields.String(default=None),
    'profile': fields.Nested(public_profile_fields, default=None),
}
