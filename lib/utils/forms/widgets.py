# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.forms.widgets import ChoiceFieldRenderer, RendererMixin, ChoiceInput
from django.template import loader
from django.utils.encoding import force_str, force_text
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from ..html import Icon, AttributeDict


class IconInputMixin(object):
    """
    A widget to render an input with icon.

    Can render in two ways, the simplest with the icon inside the input,
    the other with the icon coupled to the input.
    """
    _errors = {
        'invalid_icon': _("'%s' object is not a Icon or str object."),
        'invalid_format': _("'%s' format is not valid."),
        'invalid_side': _("'%s' side is not valid."),
    }

    ON_LEFT = "left"
    ON_RIGHT = "right"

    _ON = {ON_LEFT: 'prepend', ON_RIGHT: 'append'}

    FORMAT_ADD_ON = "addon"
    FORMAT_GROUP = "group"
    FORMAT_ICON = "icon"

    def __init__(self, icon, format="icon", on="right", attrs=None, *args, **kwargs):
        attrs = AttributeDict(attrs or {})
        super(IconInputMixin, self).__init__(attrs=attrs, *args, **kwargs)

        assert isinstance(icon, (basestring, Icon)), \
            self._errors['invalid_icon'] % (type(icon).__name__,)

        assert format in [
            self.FORMAT_ADD_ON,
            self.FORMAT_GROUP,
            self.FORMAT_ICON
        ], self._errors['invalid_format'] % (format,)

        assert on in [self.ON_LEFT, self.ON_RIGHT], \
            self._errors['invalid_side'] % (on,)

        icon = Icon(icon) if isinstance(icon, basestring) else icon  # grant is a .Icon object

        self._format = format
        self._on = on
        self._icon = icon

    def _get_icon(self):
        if self._format == IconInputMixin.FORMAT_ICON:
            self._icon.attrs.add_class('icon-' + self._ON[self._on])
        return self._icon

    icon = property(_get_icon)

    def _get_template(self):
        render_format = self._format
        render_on = self._on

        fa = IconInputMixin.FORMAT_ADD_ON
        fg = IconInputMixin.FORMAT_GROUP
        fi = IconInputMixin.FORMAT_ICON
        ol = IconInputMixin.ON_LEFT
        ot = IconInputMixin.ON_RIGHT

        if render_format == fg and render_on == ol:
            return '<div class="input-group"><span class="input-group-addon">' \
                   '{{ icon }}</span>{{ input }}</div>'
        if render_format == fg and render_on == ot:
            return '<div class="input-group">{{ input }}<span class="' \
                   'input-group-addon">{{ icon }}</span></div>'
        elif render_format == fa:
            return '<span class="input-icon-' + render_on + \
                   '">{{ icon }}{{ input }}</span>'
        elif render_format == fi:
            return '<label class="input">{{ icon }}{{ input }}</label>'

        return ''

    html_output_format = property(_get_template)

    def html_output(self, rendered_input):
        t = loader.get_template_from_string(self.html_output_format)
        c = loader.Context({
            'input': rendered_input,
            'icon': self.icon.as_html()
        })
        return mark_safe(t.render(c))

    def render(self, name, value, attrs=None):
        rendered_input = super(IconInputMixin, self).render(name, value, attrs)
        return self.html_output(rendered_input)


# <editor-fold desc="IconInputs">
class TextIconInput(IconInputMixin, forms.TextInput):
    """Text input with a icon"""


class PasswordIconInput(IconInputMixin, forms.PasswordInput):
    """Password input with a icon"""


class EmailIconInput(IconInputMixin, forms.EmailInput):
    """Email input with a icon"""

    DEFAULT_ATTRS = {
        'size': 25,
    }

    def __init__(self, attrs=None, *args, **kwargs):
        icon = kwargs.get('icon') or Icon('envelope')
        render_format = kwargs.get('format') or "group"

        _attrs, attrs = (attrs or {}).copy(), self.DEFAULT_ATTRS

        super(EmailIconInput, self).__init__(
            icon=icon, format=render_format, attrs=attrs, *args, **kwargs
        )

        # update defaults
        for key, value in _attrs.items():
            self.attrs.attr(key, value)
# </editor-fold>


class DateInput(IconInputMixin, forms.DateInput):
    DEFAULT_ATTRS = {
        'class': 'datepicker',
        'data-date-format': 'dd/mm/yyyy',
        'size': 13,
        'data-mask': 'date'
    }

    input_type = 'date'

    def __init__(self, attrs=None, *args, **kwargs):
        icon = Icon('calendar')
        render_format = "group"
        render_on = "right"
        _attrs, attrs = (attrs or {}).copy(), self.DEFAULT_ATTRS

        super(DateInput, self).__init__(
            icon=icon, format=render_format,
            on=render_on, attrs=attrs, *args, **kwargs
        )

        # update defaults
        for key, value in _attrs.items():
            self.attrs.attr(key, value)


class CheckboxInput(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        attrs = AttributeDict(attrs or {})
        attrs.add_class("checkbox style-2")
        checkbox = super(CheckboxInput, self).render(name, value, attrs=attrs)
        return mark_safe('<label class="checkbox-inline">%s<span class="lbl"></span></label>' % checkbox)


class RadioInput(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        attrs = AttributeDict(self.build_attrs(attrs, type='radio', name=name))
        attrs.add_class('radiobox style-2')
        if self.check_test(value):
            attrs.attr('checked', 'checked')
        if not (value is True or value is False or value is None or value == ''):
            # Only add the 'value' attribute if a value is non-empty.
            attrs['value'] = force_str(value)
        return mark_safe('<input %s />' % attrs.as_html())


# <editor-fold desc="Select">
class InlineRadioSelect(forms.RadioSelect):
    output_html = '<label class="radio radio-inline">{{ field }}<span class="lbl">{{ label }}</span></label>'

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = AttributeDict(attrs or {})
        attrs.add_class('ace')
        super(InlineRadioSelect, self).__init__(attrs, *args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        output = []

        value = force_str(value) or ''

        attrs = self.build_attrs(attrs)
        t = loader.get_template_from_string(self.output_html)

        for id, label in list(chain(self.choices, choices)):
            check = lambda v: force_str(v) in value
            radio = RadioInput(attrs, check_test=check)
            output.append(t.render(loader.Context({
                "field": radio.render(name, id),
                "label": mark_safe("%s" % label)
            })))

        return mark_safe("&nbsp;&nbsp;&nbsp;&nbsp;".join(output))


class SelectChosen(forms.Select):
    def __init__(self, *args, **kwargs):
        super(SelectChosen, self).__init__(*args, **kwargs)
        self.attrs = AttributeDict(self.attrs)
        self.attrs.add_class("chosen-select")


class ActionSelect(forms.Select):
    def __init__(self, create_viewname=None, create_original_title=None, list_viewname=None, group_data_label=None,
                 *args, **kwargs):
        self.group_data_label = group_data_label or _('Values')
        self.create_viewname = create_viewname
        self.list_viewname = list_viewname
        self.create_original_title = create_original_title or _('Create:')
        super(ActionSelect, self).__init__(*args, **kwargs)

    def get_action_group(self):
        if self.list_viewname or self.create_viewname:
            output = [format_html('<optgroup{0}>', flatatt({'label': _('Actions')}))]
            if self.create_viewname:
                output.append('<option ' + AttributeDict({
                    'data-action': reverse(self.create_viewname),
                    'data-original-title': self.create_original_title,
                    'value': 'aN'
                }).as_html() + '>')
                output.append(':: ' + _('Add New'))
                output.append('</option>')

            if self.list_viewname:
                output.append('<option ' + AttributeDict({
                    'data-action': reverse(self.list_viewname),
                    'value': 'lA'
                }).as_html() + '>')
                output.append(':: ' + _('Manage All'))
                output.append('</option>')

            output.append('</optgroup>')
            return '\n'.join(output)
        return ''

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name, rel='select')
        output = [format_html('<select{0}>', flatatt(final_attrs))]

        actions = self.get_action_group()

        choices = []

        has_blank_choice = False
        blank_choice = None
        for v, l in self.choices:
            if v:
                choices.append((v, l))
                continue
            blank_choice = l
            has_blank_choice = True

        if has_blank_choice:
            self.choices = tuple()
            output.append('<option>' + blank_choice + '</option>')

        if actions:
            output.append(actions)

        options = self.render_options(choices, [value])
        if options:
            output.append('<optgroup label="' + self.group_data_label + '">' +
                          options + '</optgroup>')
        output.append('</select>')
        return mark_safe('\n'.join(output))


class EmptySelect(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        self.choices = tuple()
        return super(EmptySelect, self).render(name, value, attrs=attrs, choices=())

# </editor-fold>


# <editor-fold desc="SelectMultiple">
class CheckBoxChoiceInput(ChoiceInput):
    input_type = 'checkbox'

    def __init__(self, *args, **kwargs):
        super(CheckBoxChoiceInput, self).__init__(*args, **kwargs)
        self.value = force_text(self.value)

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)

        final_attrs = dict(self.attrs, type=self.input_type, name=self.name, value=self.choice_value)
        final_attrs = AttributeDict(final_attrs)
        final_attrs.add_class("checkbox style-2")

        if self.is_checked():
            final_attrs.attr('checked', 'checked')

        return format_html('<label><input{0} /><span class="lbl">{1}</span></label>', flatatt(final_attrs), self.choice_label)

    def render(self, name=None, value=None, attrs=None, choices=()):
        return self.tag()


class CheckboxFieldRenderer(ChoiceFieldRenderer):
    choice_input_class = CheckBoxChoiceInput

    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)
        ul_attrs = AttributeDict({"class": "checkbox-select"})

        if id_ is not None:
            ul_attrs.attr('id', id_)

        start_tag = format_html('<ul {0}>', ul_attrs.as_html())
        output = [start_tag]
        for widget in self:
            output.append(format_html('<li>{0}</li>', force_text(widget)))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class CheckboxSelectMultiple(RendererMixin, forms.SelectMultiple):
    renderer = CheckboxFieldRenderer
    _empty_value = []
# </editor-fold>


