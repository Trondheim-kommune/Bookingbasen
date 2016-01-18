# -*- coding: utf-8 -*-
from flask.ext.restful import fields


class ISO8601DateTime(fields.Raw):
    def __init__(self, default=None, attribute=None):
        super(ISO8601DateTime, self).__init__(default, attribute)

    def format(self, value):
        if not value:
            return self.default
        return value.isoformat()

