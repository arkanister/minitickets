# -*- coding: utf-8 -*-

import re
from django.core.exceptions import ValidationError

from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


DV_MOD10 = lambda x: 1 if x == 10 else x
DV_MOD11 = lambda x: 11 - x if x >= 2 else 0


class BaseValidator(object):
    code = 'invalid'
    regex = r''
    real_size = None

    def compare_format(self, value):
        """
        Validates that the input matches the regular expression.
        """
        return bool(self.regex.match(value))

    def compare_digits(self, value):
        try:
            int(value)  # try to convert to int
        except ValueError:
            return False
        return True

    def compare_size(self, value):
        return len(value) == self.real_size

    def __call__(self, value):

        if value in EMPTY_VALUES:
            return

        if not self.compare_format(value):
            raise ValidationError(self.default_error_messages['invalid'])

        if not value.isdigit():
            value = re.sub('[-\.]', '', value)

        if not self.compare_digits(value):
            raise ValidationError(self.default_error_messages['invalid'])

        if not self.compare_size(value):
            raise ValidationError(self.default_error_messages['max_digits'])

        if not self.compare_dv(value):
            raise ValidationError(self.default_error_messages['invalid_dv'])


class CpfValidator(BaseValidator):
    regex = re.compile(r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$')
    real_size = 11
    default_error_messages = {
        'invalid': _("Invalid CPF format."),
        'max_digits': _("This field should only contain 11 digits."),
        'invalid_dv': _("Invalid CPF.")
    }

    def compare_dv(self, value):
        orig_dv = value[-2:]
        new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -1))])
        new_1dv = DV_MOD11(new_1dv % 11)
        value = value[:-2] + str(new_1dv) + value[-1]
        new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -1))])
        new_2dv = DV_MOD11(new_2dv % 11)
        value = value[:-1] + str(new_2dv)
        return value[-2:] == orig_dv


class CnpjValidator(BaseValidator):
    regex = re.compile(r'^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$')
    real_size = 14
    default_error_messages = {
        'invalid': _("Invalid CNPJ format."),
        'max_digits': _("This field should only contain 11 digits."),
        'invalid_dv': _("Invalid CNPJ.")
    }

    def compare_dv(self, value):
        orig_dv = value[-2:]
        new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(5, 1, -1) + range(9, 1, -1))])
        new_1dv = DV_MOD11(new_1dv % 11)
        value = value[:-2] + str(new_1dv) + value[-1]
        new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(6, 1, -1) + range(9, 1, -1))])
        new_2dv = DV_MOD11(new_2dv % 11)
        value = value[:-1] + str(new_2dv)
        return value[-2:] == orig_dv


class BirthCertificateValidator(BaseValidator):
    regex = re.compile(r'^(\d{6})\.((\d{2})\.){2}(\d{4})\.(\d)\.(\d{5})\.(\d{3})\.(\d{7})\-(\d{2})$')
    real_size = 32
    default_error_messages = {
        'invalid': _("Invalid birth certificate format."),
        'max_digits': _("This field should only contain 32 digits."),
        'invalid_dv': _("Invalid birth certificate.")
    }

    def compare_dv(self, value):
        dv, value = value[-2:], value[:-2]
        dv_1 = DV_MOD10(sum([v * (int(value[i]) if not i in [8, 9, 14] else 0) for i, v in enumerate(range(2, 11) + range(0, 11) + range(0, 10))]) % 11)
        value = "%s%d" % (value, dv_1)
        dv_2 = DV_MOD10(sum([v * (int(value[i]) if not i in [8, 9, 14] else 0) for i, v in enumerate(range(1, 11) + range(0, 11) + range(0, 10))]) % 11)
        dv_calc = "%d%d" % (dv_1, dv_2)
        return dv == dv_calc