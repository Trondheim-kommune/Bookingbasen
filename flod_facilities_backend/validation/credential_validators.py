# -*- coding: utf-8 -*-
from flask import request, current_app

from domain.models import Image, Document
from validation.base_validators import ParameterizedValidator
import repo


class CanCreateFacilityValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):
        user_id = repo.get_user_id_for_user(cookies=request.cookies)
        valid = user_id and repo.can_user_create_facility(user_id, cookies=request.cookies)
        if not valid:
            self.fail("You do not have privileges to create a facility.",
                      f, 403, None, *args, **kwargs)


class CanEditFacilityValidator(ParameterizedValidator):
    def validate(self, f, *args, **kwargs):


        if kwargs.get("facility_id", None):  # the normal case: a faility
            facility_id = kwargs["facility_id"]
        elif kwargs.get("image_id", None):  # an image related to a facility
            image = current_app.db_session.query(Image).get(kwargs["image_id"])
            facility_id = image.facility_id
        elif kwargs.get("document_id", None):  # a document related to a facility
            document = current_app.db_session.query(Document).get(kwargs["document_id"])
            facility_id = document.facility_id
        elif request.form.get('facilityId', None):  # POST image/document with facility id in form
            facility_id = request.form.get('facilityId')
        #this should cover all cases where this decorator is used

        user_id = repo.get_user_id_for_user(cookies=request.cookies)
        valid = user_id and repo.can_user_edit_facility(user_id, facility_id,
                                                        cookies=request.cookies)
        if not valid:
            self.fail("You do not have privileges to edit facility %s." % facility_id,
                      f, 403, None, *args, **kwargs)

