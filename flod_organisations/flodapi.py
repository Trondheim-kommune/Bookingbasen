# -*- coding: utf-8 -*-
from flask import jsonify, current_app
from flask.ext.restful import Api

from validation.base_validators import ValidationException


class FlodApi(Api):
    ## OBS: the @app.errorhandler is not the right way to configure the custom error handlers
    ## when the endpoint is a flask-restful endpoint instead of a standard flask endpoint
    ## more about it in flask_restful.__init__.error_router
    def handle_validation_exception(self, exception):
        response = jsonify(exception.to_dict())
        response.status_code = exception.status_code
        current_app.logger.warn("Validation exception occured:\n  Statuscode=%s\n  Response=%s"
                                % (response.status_code, str(exception.to_dict())))
        return response

    def handle_error(self, e):
        if isinstance(e, ValidationException):
            return self.handle_validation_exception(e)
        else:
            # for all other errors use flask-restful's default error handling.
            return super(FlodApi, self).handle_error(e)
