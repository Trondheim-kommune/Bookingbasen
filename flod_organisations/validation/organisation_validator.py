# -*- coding: utf-8 -*-
from flod_common.validation.base_validator import BaseValidator
from validation.address_validator import AddressValidator


class OrganisationValidator(BaseValidator):
    '''
    Validator klasse for OrganisationValidator
    '''

    def validate_put_fields(self):
        self.validate_is_defined('name',label='Aktørens navn')

        self.validate_is_norwegian_phone_number('phone_number', label="Telefonnummer")
        self.validate_is_norwegian_phone_number('telefax_number', 'Telefaxnummer må være 8 siffer', requires_value=False)
        self.validate_is_email('email_address', label='E-post')

        if self.data.get('postal_address'):
            self.validate_sub_values_for_dict('postal_address', AddressValidator)

        if self.data.get('business_address'):
            self.validate_sub_values_for_dict('business_address', AddressValidator)

        self.validate_extra_fields()
        return self

    def validate_extra_fields(self):
        self.validate_is_email('local_email_address', label='E-post 2', requires_value=False)
        if self.data.get('tilholdssted_address'):
            self.validate_sub_values_for_dict('tilholdssted_address', AddressValidator)

        return self

    def validate_post_fields(self):
        self.validate_put_fields()

        return self