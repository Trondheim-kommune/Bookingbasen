# -*- coding: utf-8 -*-
import json

from flask import current_app, request
from flask.ext.restful import abort
from sqlalchemy.orm.exc import NoResultFound
import requests


class UriResourceGetter(object):
    def __init__(self, root_url, resource_type, resource_name):
        self.root_url = root_url
        self.resource_type = resource_type
        self.resource_name = resource_name

    def get_for_uri(self, uri, cookies=None):
        try:
            return current_app.db_session.query(self.resource_type).filter(self.resource_type.uri == uri).one()
        except NoResultFound:
            return self.copy_from_web(uri, cookies=cookies)

    def copy_from_web(self, uri, cookies=None):
        content = self.get_from_web(uri, cookies=cookies)
        uri = content["uri"]
        resource = self.resource_type(uri=uri)
        current_app.db_session.add(resource)
        current_app.db_session.commit()
        current_app.db_session.refresh(resource)
        return resource

    def get_from_web(self, uri, cookies=None):
        url = self.root_url + uri
        if cookies is None:
            cookies = request.cookies
        response = requests.get(url, cookies=cookies)
        if response.status_code == 200:
            return json.loads(response.content)
        abort(404, __error__=["No %s found." % self.resource_name])
