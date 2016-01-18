#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Wrapper module for itsdangerous. It's used for creating signed authentication
tokens, with an optional expiration time.
"""

import os

from itsdangerous import BadSignature, URLSafeTimedSerializer


# Secret used to sign security tokens
AUTH_TOKEN_SECRET = os.environ['AUTH_TOKEN_SECRET']

# Username for the superuser
ADMIN_USER_ID = os.environ['AUTH_ADMIN_USER_ID']

# Default max age for security tokens in seconds
MAX_AGE = 604800  # 1 week


def make_auth_token(username):
    """Create a regular token for the given username"""
    s = URLSafeTimedSerializer(AUTH_TOKEN_SECRET)
    return s.dumps(username)


def make_superuser_auth_token():
    """Create a superuser token"""
    return make_auth_token(ADMIN_USER_ID)


def unsign_auth_token(auth_token, max_age=MAX_AGE):
    """Unsign given auth_token and return the deserialized value. The max_age
    parameter sets the maximum allowed age of the token.
    """
    if auth_token is None:
        return None
    s = URLSafeTimedSerializer(AUTH_TOKEN_SECRET)
    try:
        return s.loads(auth_token, max_age=max_age)
    except (BadSignature, TypeError):
        return None


def verify_auth_token(auth_token, max_age=MAX_AGE):
    """Verify given auth_token. Returns True if the token is valid."""
    return unsign_auth_token(auth_token, max_age=max_age) is not None


def verify_superuser_auth_token(auth_token, max_age=MAX_AGE):
    """Verify given auth_token. Returns True if the token is valid and the user
    is a superuser.
    """
    username = unsign_auth_token(auth_token, max_age=max_age)
    return username == ADMIN_USER_ID


def make_auth_cookie(username):
    """Create an security cookie for the given username. Does the same thing as
    make_auth_token and wraps the token in a dict suitable for use with Flask
    and requests.
    """
    return {'auth_token': make_auth_token(username)}


def make_superuser_auth_cookie():
    """Does the same as make_auth_cookie, excepts it creates the cookie for the
    superuser instead.
    """
    return {'auth_token': make_superuser_auth_token()}
