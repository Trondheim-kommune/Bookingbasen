# -*- coding: utf-8 -*-

from api.credential_resource import CredentialResource
from api.flodapi import FlodApi
from api.public_user_resource import PublicUserResource
from api.user_profile_resource import UserProfileResource
from api.user_resource import UserResource, RoleResource


def create_api(app, api_version):
    api = FlodApi(app)

    api.add_resource(
        UserResource,
        '/api/%s/users/' % api_version,
        '/api/%s/users/<string:user_id>' % api_version
    )

    api.add_resource(
        PublicUserResource,
        '/api/%s/users/public' % api_version,
        '/api/%s/users/<string:user_id>/public' % api_version
    )

    api.add_resource(
        RoleResource,
        '/api/%s/users/<string:user_id>/roles' % (api_version,)
    )

    api.add_resource(
        UserProfileResource,
        '/api/%s/users/<string:user_id>/profile' % api_version
    )

    api.add_resource(
        CredentialResource,
        '/api/%s/credentials/' % api_version,
        '/api/%s/credentials/<string:credential_id>' % api_version,
        '/api/%s/users/<string:user_id>/credentials/<string:credential_id>' % api_version
    )

    return api
