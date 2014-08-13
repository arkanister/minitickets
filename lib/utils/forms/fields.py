# -*- coding: utf-8 -*-

import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from itertools import groupby
from django.forms.models import ModelChoiceIterator


from .widgets import DateInput, InputIconWidget
from ..html import Icon, AttributeDict


# <editor-fold desc="RG">
class RGWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        widgets = (forms.TextInput(attrs={"placeholder": "Número", "size": 15, "maxlength": 11, "class": "input-mask-rg"}),
                   forms.TextInput(attrs={"placeholder": "Orgão Emissor", "maxlength": 14, "size": 11, "class": "input-mask-rg-orgao-emissor input-key-up"}),
                   DateInput(attrs={"placeholder": "Emissão", "size": 10}))
        super(RGWidget, self).__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        return u'<div class="fields-g">%s%s%s</div>' % tuple(rendered_widgets)

    def decompress(self, value):
        if not value:
            return [None, None, None]
        return value.split(' ')


class RGField(forms.MultiValueField):

    widget = RGWidget

    def __init__(self, label='RG', fields=None, *args, **kwargs):
        fields = (forms.CharField(), forms.CharField(), forms.DateField())
        super(RGField, self).__init__(label=label, fields=fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] in EMPTY_VALUES:
            raise forms.ValidationError(u'Número do RG em formato incorreto.')
        if data_list[1] in EMPTY_VALUES:
            raise forms.ValidationError(u'Orgão Emissor do RG em formato incorreto.')
        if data_list[2] in EMPTY_VALUES:
            raise forms.ValidationError(u'Data de Emissão do RG em formato incorreto.')

        data_list[2] = data_list[2].strftime("%d/%m/%Y")

        return '%s %s %s' % tuple(data_list)
# </editor-fold>


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


class CpfField(forms.CharField):

    default_error_messages = {
        'invalid': "Número de CPF Inválido.",
        'digits_only': "Este campo requer apenas números.",
        'max_digits': "Este campo deve conter apenas 11 digitos.",
    }

    BASE_ATTRS = {"class": "input-mask-cpf"}



    def clean(self, value):
        value = super(CpfField, self).clean(value)
        orig_value = value

        """
        Value can be either a string in the format XXX.XXX.XXX-XX or an
        11-digit number.
        """
        if value in EMPTY_VALUES:
            return u''
        if not value.isdigit():
            value = re.sub("[-\.]", "", value)

        try:
            int(value)
        except ValueError:
            raise ValidationError(self.error_messages['digits_only'])

        if len(value) != 11:
            raise ValidationError(self.error_messages['max_digits'])
        orig_dv = value[-2:]

        new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -1))])
        new_1dv = DV_maker(new_1dv % 11)
        value = value[:-2] + str(new_1dv) + value[-1]
        new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -1))])
        new_2dv = DV_maker(new_2dv % 11)
        value = value[:-1] + str(new_2dv)
        if value[-2:] != orig_dv:
            raise ValidationError(self.error_messages['invalid'])

        return orig_value


class CnpjField(forms.CharField):
    default_error_messages = {
        'invalid': "Número de CNPJ Inválido.",
        'digits_only': "Este campo requer apenas números.",
        'max_digits': "Este campo deve conter apenas 14 digitos.",
    }

    def clean(self, value):
        value = value = super(CnpjField, self).clean(value)
        orig_value = value
        # Try to Validate CNPJ
        """
        Value can be either a string in the format XX.XXX.XXX/XXXX-XX or a
        group of 14 characters.
        """
        if value in EMPTY_VALUES:
            return u''
        if not value.isdigit():
            value = re.sub("[-/\.]", "", value)
        try:
            int(value)
        except ValueError:
            raise ValidationError(self.error_messages['digits_only'])
        if len(value) != 14:
            raise ValidationError(self.error_messages['max_digits'])
        orig_dv = value[-2:]

        new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(5, 1, -1) + range(9, 1, -1))])
        new_1dv = DV_maker(new_1dv % 11)
        value = value[:-2] + str(new_1dv) + value[-1]
        new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(6, 1, -1) + range(9, 1, -1))])
        new_2dv = DV_maker(new_2dv % 11)
        value = value[:-1] + str(new_2dv)
        if value[-2:] != orig_dv:
            raise ValidationError(self.error_messages['invalid'])

        return orig_value


class CertidaoNascimentoField(forms.CharField):

    default_error_messages = {
        'invalid': "Certidão de nascimento inválida.",
        'digits_only': "Este campo requer apenas números.",
        'max_digits': "Este campo deve conter apenas 40 digitos.",
    }

    def dv_is_valid(self, value):
        """
        Check dv is valid.
        """
        def dv_maker(dv):
            return 1 if dv == 10 else dv
        dv, value = value[-2:], value[:-2]

        dv_1 = dv_maker(sum([v * (int(value[i]) if not i in [8, 9, 14] else 0) for i, v in enumerate(range(2, 11) + range(0, 11) + range(0, 10))]) % 11)
        value = "%s%d" % (value, dv_1)
        dv_2 = dv_maker(sum([v * (int(value[i]) if not i in [8, 9, 14] else 0) for i, v in enumerate(range(1, 11) + range(0, 11) + range(0, 10))]) % 11)
        dv_calc = "%d%d" % (dv_1, dv_2)
        return dv == dv_calc

    def clean(self, value):
        value = super(CertidaoNascimentoField, self).clean(value)
        # Try to validate certidão de nascimento
        """
        Value can be either a string in the
        format XXXXXX.XX.XX.XXXX.X.XXXXX.XXX.XXXXXXX-XX or
        regex r'^(\d{6})\.((\d{2})\.){2}(\d{4})\.(\d)\.(\d{5})\.(\d{3})\.(\d{7})\-(\d{2})$'
        with 42 charaters.
        """

        if value in EMPTY_VALUES:
            return u''

        regex = r'^(\d{6})\.((\d{2})\.){2}(\d{4})\.(\d)\.(\d{5})\.(\d{3})\.(\d{7})\-(\d{2})$'
        if not bool(re.match(regex, value)):
            raise ValidationError(self.error_messages['invalid'])

        striped_value = re.sub("[-/\.]", "", value)

        try:
            int(striped_value)
        except ValueError:
            raise ValidationError(self.error_messages['digits_only'])

        if not self.dv_is_valid(striped_value):
            raise ValidationError(self.error_messages['invalid'])

        if len(value) != 40:
            raise ValidationError(self.error_messages['max_digits'])

        return value


# LOGRADOURO FIELD
class LogradouroWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        widgets = (forms.TextInput(attrs={"placeholder": "Rua/Avenida/Travessa", "size": 35,}),
                   forms.TextInput(attrs={"placeholder": "Número", "size": 8}))
        super(LogradouroWidget, self).__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        return u'<div class="fields-g">%s%s</div>' % tuple(rendered_widgets)

    def decompress(self, value):
        if not value:
            return [None, None]
        return value.split(', ')


class LogradouroField(forms.MultiValueField):

    widget = LogradouroWidget

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(),
                  forms.IntegerField())
        super(LogradouroField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if not data_list:
            return None
        if data_list[0] in EMPTY_VALUES:
            raise forms.ValidationError(u'Logradouro Inválido.')
        if data_list[1] in EMPTY_VALUES:
            raise forms.ValidationError(u'Número Inválido.')
        return '%s, %s' % tuple(data_list)


# GROUPED FIELD
class GroupedModelChoiceField(forms.ModelChoiceField):

    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        """
        group_by_field is the name of a field on the model
        group_label is a function to return a label for each choice group
        """
        super(GroupedModelChoiceField, self).__init__(*args, **kwargs)
        self.group_by_field = group_by_field
        if group_label is None:
            self.group_label = lambda group: group
        else:
            self.group_label = group_label

    def _get_choices(self):
        """
        Exactly as per ModelChoiceField except returns new iterator class
        """
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self)
    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


class GroupedModelChoiceIterator(ModelChoiceIterator):

    def __iter__(self):

        if self.field.empty_label is not None:
            yield (u"", self.field.empty_label)

        if self.field.cache_choices:

            if self.field.choice_cache is None:

                self.field.choice_cache = [
                    (self.field.group_label(group), [self.choice(ch) for ch in choices])
                        for group, choices in groupby(self.queryset.all(),
                            key=lambda row: getattr(row, self.field.group_by_field))
                ]
            for choice in self.field.choice_cache:
                yield choice

        else:
            for group, choices in groupby(self.queryset.all(),
                    key=lambda row: getattr(row, self.field.group_by_field)):
                yield (self.field.group_label(group), [self.choice(ch) for ch in choices])


# CURRENCY AND DECIMAL FIELDS
class DecimalField(forms.DecimalField):

    def __init__(self, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)
        self.localize = True
        self.widget.is_localized = True


class CurrencyField(DecimalField):
    def __init__(self, *args, **kwargs):
        widget = kwargs.get('widget', None)
        if not widget:
            widget = InputIconWidget(
                Icon(name=None, html_tag='b', content='R$'),
                render_type=InputIconWidget.INPUT_GROUP,
                side=InputIconWidget.ICON_ON_LEFT,
                attrs={'size': 13, 'class': 'align-right input-mask-currency'}
            )
        kwargs['widget'] = widget
        super(CurrencyField, self).__init__(*args, **kwargs)