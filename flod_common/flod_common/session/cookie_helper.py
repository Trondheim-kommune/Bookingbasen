# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
from flod_common.session.redirect_helper import get_redirect_target, is_safe_url

DEBUG = os.environ.get('DEBUG') == 'True'


def set_redirect_target_cookie(response):
    redirect_target = get_redirect_target()
    if redirect_target:
        set_cookie(response, "redirect_target", redirect_target)


def get_redirect_target_from_cookie(request):
    redirect_target = request.cookies.get("redirect_target", None)
    if not redirect_target or not is_safe_url(redirect_target):
        redirect_target = None
    return redirect_target


def invalidate_redirect_target_cookie(response):
    # Invalidate the redirect cookie by giving it a past expiry date
    set_cookie(response, "redirect_target", "", max_age=0)


def set_auth_type_cookie(response, auth_type):
    max_age = 365 * 24 * 60 * 60
    set_cookie(response, 'authentication_type', auth_type, max_age=max_age)


def get_auth_type_from_cookie(request):
    return request.cookies.get('authentication_type', None)


def set_cookie(response, key, content, max_age=None):
    """Use HTTPS only cookies in non-debug mode.

        NOTE: HTTPS does not work on dev/test/CI!
    """
    expires = datetime.now() + timedelta(seconds=max_age) if max_age is not None else None
    if DEBUG:
        response.set_cookie(key, content, httponly=True, max_age=max_age, expires=expires)
    else:
        response.set_cookie(key, content, httponly=True, secure=True, max_age=max_age, expires=expires)