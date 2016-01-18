# -*- coding: utf-8 -*-
from datetime import datetime
from validate_email import validate_email

import re


class BaseValidator(object):
    """
    Validator utility klasse med støtte for chaining av valideringer
    """

    def __init__(self, data):
        self.errors = {}
        self.data = data

    def has_errors(self):
        return len(self.errors) > 0

    def add_error(self, error_key, error_value):
        """
        OBS: Hvis det allerede finnes en error med error_key som nøkkel blir dens verdi overskrevet med error_value
        :param error_key:
        :param error_value:
        :return:
        """
        self.errors[error_key] = error_value

    def add_errors(self, errors_dict):
        """
        OBS: Dataene overskrives når det allerede finnes en elementer i self.errors med de samme nøkklene som i errors_dict.
        :param errors_dict: dictionary av error som legges til self.errors
        :return:
        """
        if len(errors_dict) > 0:
            self.errors.update(errors_dict)

    def validate_le_max_length(self, key_name, max_length, msg_key=None):
        """
        Validerer at value for dictionary objektet med "key_name" som nøkke er mindre eller lik "max_length"
        :param key_name: nøkkelen til objektet som slås opp
        :param max_length: max_length
        :param msg_key: dersom denne settes, brukes denne i stedet for key_name i valideringsfeilmeldingen.
        :return:
        """
        if self.data.get(key_name) and not (len(self.data.get(key_name)) <= max_length):
            self.errors[key_name] = 'Maks lengde for %s er %d tegn' % (msg_key if msg_key else key_name, max_length)

        return self

    def validate_dates_are_ordered(self, date1_key_name, date2_key_name, msg):
        if self.data.get(date1_key_name) and not self.data.get(date2_key_name):
            self.errors[date2_key_name] = 'Sluttdato mangler'
        if self.data.get(date2_key_name) and not self.data.get(date1_key_name):
            self.errors[date1_key_name] = 'Startdato mangler'
        if self.data.get(date1_key_name) and self.data.get(date2_key_name):
            date1 = datetime.strptime(self.data.get(date1_key_name), "%Y-%m-%d").date()
            date2 = datetime.strptime(self.data.get(date2_key_name), "%Y-%m-%d").date()
            if date1 > date2:
                if msg:
                    self.add_error(date1_key_name, msg)
                else:
                    self.add_error(date1_key_name, '%s må være før %s' % (date1_key_name, date2_key_name))
        return self

    def validate_not_equals(self, key_name, compare_to_str, msg=None):
        value = self.data.get(key_name)
        if value and value == compare_to_str:
            if msg:
                self.errors[key_name] = msg
            else:
                self.errors[key_name] = "Verdien i '%s' skal ikke være '%s' " % (key_name, compare_to_str)
        return self

    def validate_is_defined(self, key_name, label=None):
        value = self.data.get(key_name)
        if not value:
            self.errors[key_name] = "%s må fylles ut" % (label if label is not None else key_name)
        return self

    def validate_is_norwegian_phone_number(self, key_name, error_msg=None, label=None, requires_value=True):
        telefonnr = self.data.get(key_name)
        if not telefonnr:
            if requires_value:
                self.errors[key_name] = "%s må fylles ut" % (label if label is not None else key_name) if error_msg is None else error_msg
                return self
            else:
                return self

        if not (len(telefonnr) == 8 and telefonnr.isdigit()):
            self.errors[key_name] = 'Telefonnummer må være 8 siffer' if error_msg is None else error_msg
        return self

    def validate_is_norwegian_bank_account_number(self, key_name):
        req_length = 11
        no_bank_account_number = self.data.get(key_name)
        if no_bank_account_number and not (
                        len(no_bank_account_number) == req_length and no_bank_account_number.isdigit()):
            self.errors[key_name] = 'Kontonummer må være %d siffer' % req_length
        return self

    def  validate_is_email(self, key_name, label=None, requires_value=True):
        email = self.data.get(key_name)
        if not email:
            if requires_value:
                self.errors[key_name] = "%s må fylles ut" % (label if label is not None else key_name)
                return self
            else:
                return self

        if not validate_email(email):
            self.errors[key_name] = "Ugyldig epostadresse"
        return self

    def validate_is_name(self, key_name, label, requires_value=True):
        name = self.data.get(key_name)
        if not name:
            if requires_value:
                self.errors[key_name] = "%s må fylles ut" % (label if label is not None else key_name)
                return self
            else:
                return self
        if not name.replace('-', ' ').replace(' ', '').isalpha():
            self.errors[key_name] = "Ugyldig %s" % label
        return self

    def is_postal_code_valid(self, postal_code, key_name):
        if not re.match("^\d{4}$", postal_code):
            self.errors[key_name] = "Ugyldig postnummer"
        return self

    def validate_is_positive_integer(self, key_name, msg_key=None, requires_value=True):
        value = self.data.get(key_name)
        if value is None:
            if requires_value:
                self.errors[key_name] = "%s må fylles ut" % (msg_key if msg_key is not None else key_name)
                return self
            else:
                return self
        if isinstance(value, basestring) and value.isdigit():
            value = int(value)
        if not (isinstance(value, int) and value >= 0):
            self.errors[key_name] = "%s må være heltall større eller lik 0" % (
            msg_key if msg_key is not None else key_name)
        return self

    def validate_all_sub_values(self, iterable_key_name, validator_class):
        if self.data.get(iterable_key_name):
            for idx, item in enumerate(self.data.get(iterable_key_name)):
                validator = validator_class(item)
                validator.validate_put_fields()
                if validator.has_errors():

                    error = self.errors.get(iterable_key_name)
                    if error is None:
                        error = {}
                    error[idx] = validator.errors

                    errors = {iterable_key_name: error}
                    self.add_errors(errors)
        return self

    def validate_sub_values_for_dict(self, key_name, validator_class):
        validator = validator_class(self.data.get(key_name))
        validator.validate_put_fields()
        if validator.has_errors():
            self.add_errors({key_name: validator.errors})

        return self

    def validate_max_value(self, key_name, max_value):
        if self.data.get(key_name) and not (int(self.data.get(key_name)) <= max_value):
            self.errors[key_name] = 'Maks verdi for %s er %d' % (key_name, max_value)
        return self
