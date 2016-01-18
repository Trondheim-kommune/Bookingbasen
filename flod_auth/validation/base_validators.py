# -*- coding: utf-8 -*-
from functools import wraps
import json


class ValidationException(Exception):
    def __init__(self, message, validator_name, f_module, f_name, str_args, str_kwargs,
                 status_code=400, wrapped_exceptions=None):
        Exception.__init__(self)
        self.message = message
        self.validator_name = validator_name
        self.f_module = f_module
        self.f_name = f_name
        self.str_args = str_args
        self.str_kwargs = str_kwargs
        self.status_code = status_code
        self.wrapped_exceptions = wrapped_exceptions

    def to_dict(self):
        rv = {'validator_name': self.validator_name,
              'f_module': self.f_module,
              'f_name': self.f_name,
              'str_args': self.str_args,
              'str_kwargs': self.str_kwargs,
              'message': self.message}
        if self.wrapped_exceptions and len(self.wrapped_exceptions) > 0:
            for wrapped_exception in self.wrapped_exceptions:
                if isinstance(wrapped_exception, ValidationException):
                    rv['wrapped_exception'] = json.dumps(wrapped_exception.to_dict())
                else:
                    rv['wrapped_exception'] = json.dumps(dict(wrapped_exception))
        return rv


class Validator(object):
    """
        Should be inherited and the validate mehod overridden!
    """

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            self.validate(f, *args, **kwargs)
            return f(*args, **kwargs)

        return wrapper

    def fail(self, message, f, status_code, wrapped_exceptions, *args, **kwargs):
        raise ValidationException(message,
                                  self.__class__.__name__,
                                  f.__module__,
                                  f.__name__,
                                  str(args),
                                  json.dumps(kwargs),
                                  status_code,
                                  wrapped_exceptions)

    def validate(self, f, *args, **kwargs):
        self.fail("Validator not implemented!",
                  f, 501, None, *args, **kwargs)


class ParameterizedValidator(Validator):
    """
        Should be inherited and the validate mehod overridden!
    """

    def __init__(self, *valargs, **kwvalargs):
        self.valargs = valargs
        self.kwvalargs = kwvalargs


class CollectionValidator(Validator):
    """
        Should be inherited and the validate mehod overridden!
    """

    def __init__(self, *validators):
        self.validators = validators


class NotValidator(Validator):
    def __init__(self, validator):
        self.validator = validator

    def validate(self, f, *args, **kwargs):
        try:
            self.validator.validate(f, *args, **kwargs)
        except ValidationException:
            return
        self.fail("Not applied to " + self.validator.__class__.__name__ + " failed.",
                  f, 501, None, *args, **kwargs)


class AndValidator(CollectionValidator):
    def validate(self, f, *args, **kwargs):
        for validator in self.validators:
            try:
                validator.validate(f, *args, **kwargs)
            except ValidationException, e:
                self.fail("One of the validators ran by this validator failed.",
                          f, e.status_code, [e], *args, **kwargs)


class OrValidator(CollectionValidator):
    def validate(self, f, *args, **kwargs):
        wrapped_exceptions = []
        for validator in self.validators:
            try:
                validator.validate(f, *args, **kwargs)
                return
            except ValidationException, e:
                wrapped_exceptions.append(e)
        self.fail("All the validators ran by this validator failed.",
                  f, wrapped_exceptions[0].status_code if len(wrapped_exceptions) > 0 else 400, wrapped_exceptions,
                  *args, **kwargs)

