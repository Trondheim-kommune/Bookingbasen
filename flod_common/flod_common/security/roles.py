#!/usr/bin/env python
# -*- coding: utf-8 -*-


def has_role(user, name):
    return name in (role['name'] for role in user.get('roles', []))

