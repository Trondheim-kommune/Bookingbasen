# -*- coding: utf-8 -*-
from flod_common.validation.base_validator import BaseValidator


class AddressValidator(BaseValidator):
    """
    Validator klasse for Address
    """

    def validate_put_fields(self):
        self.is_postal_code_valid(self.data['postal_code'], "postal_code")
        self.validate_is_defined('postal_city', label="Poststed")
        self.validate_is_defined('address_line', label="Addresse")

        return self
