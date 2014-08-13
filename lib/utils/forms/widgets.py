# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.template import loader
from django.utils.encoding import force_str
from django.core.urlresolvers import reverse
from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ..html import Icon, AttributeDict


class InputIconWidget(forms.widgets.Input):
    """
    A widget to render an input with icon.

    Can render in two ways, the simplest with the icon inside the input,
    the other with the icon coupled to the input.
    """

    ICON_ON_RIGHT = "right"
    ICON_ON_LEFT = "left"

    INPUT_ADDON = "addon"
    INPUT_GROUP = "group"

    SYMBOLS = ['%', 'R$']

    def __init__(self, icon, side="right", render_type="addon", input_type="text",
                 block=False, *args, **kwargs):
        self.input_type = input_type
        super(InputIconWidget, self).__init__(*args, **kwargs)

        assert isinstance(icon, (str, unicode, Icon)), "'%s' object is not a Icon or str object" % type(icon).__name__

        self.side = side
        self.render_type = render_type

        # grant is a .Icon object
        if isinstance(icon, basestring) and icon in InputIconWidget.SYMBOLS:
            icon = Icon(None, content=icon, html_tag='b')
        elif isinstance(icon, basestring):
            icon = Icon(icon)

        self.icon = icon
        self.block = block
        self.attrs = AttributeDict(self.attrs)

        if block:
            self.attrs.add_class("form-control")

    def get_template(self):
        side = self.side
        render_type = self.render_type

        template = ''

        if render_type == InputIconWidget.INPUT_GROUP and side == InputIconWidget.ICON_ON_RIGHT:
            template = '<div class="input-group">{{ input }}<span class="input-group-addon">{{ icon }}</span></div>'
        elif render_type == InputIconWidget.INPUT_GROUP and side == InputIconWidget.ICON_ON_LEFT:
            template = '<div class="input-group"><span class="input-group-addon">{{ icon }}</span>{{ input }}</div>'
        elif render_type == InputIconWidget.INPUT_ADDON:
            template = '<span class="{% if block %}block {% endif %}input-icon input-icon-' + side + \
                       '">{{ input }}{{ icon }}</span>'
        return template

    def render(self, name, value, attrs=None):
        _input = super(InputIconWidget, self).render(name, value, attrs=attrs)
        template = loader.get_template_from_string(self.get_template())
        context = loader.Context({
            "input": _input,
            "icon": mark_safe(self.icon.as_html()),
            "block": self.block
        })
        return template.render(context)


class DateInput(forms.DateInput):

    def _get_template(self):
        return '<div class="input-group">{{ input }}<span class="input-group-addon">{{ icon }}</span></div>'
    template = property(_get_template)

    def get_attrs(self, attrs=None):
        attrs = AttributeDict(attrs or {})
        attrs.add_class('datepicker')
        attrs.attr("data-date-format", "dd/mm/yyyy")
        attrs.attr("size", 13)
        return attrs

    def render(self, name, value, attrs=None):
        t = loader.get_template_from_string(self.template)
        c = loader.Context({
            "input": super(DateInput, self).render(name, value, self.get_attrs(attrs)),
            "icon": Icon('calendar', attrs={'class': 'ace-icon'}).as_html()
        })
        return t.render(c)


class CheckboxInput(forms.CheckboxInput):

    def render(self, name, value, attrs={}):
        attrs.update({"class": "ace"})
        checkbox = super(CheckboxInput, self).render(name, value, attrs=attrs)
        return mark_safe(u'<label>%s<span class="lbl"></span></label>' % checkbox)


class RadioInput(forms.CheckboxInput):

    def render(self, name, value, attrs=None):
        attrs = AttributeDict(self.build_attrs(attrs, type='radio', name=name))
        if self.check_test(value):
            attrs.attr('checked', 'checked')
        if not (value is True or value is False or value is None or value == ''):
            # Only add the 'value' attribute if a value is non-empty.
            attrs['value'] = force_str(value)
        return mark_safe('<input %s />' % attrs.as_html())


class InlineRadioSelect(forms.RadioSelect):

    output_html = '<label class="inline">{{ field }}<span class="lbl">{{ label }}</span></label>'

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
                "label": mark_safe("&nbsp;&nbsp;%s" % label)
            })))

        return mark_safe("&nbsp;&nbsp;&nbsp;&nbsp;".join(output))


# <editor-fold desc="Select">
class SelectChosen(forms.Select):

    def __init__(self, *args, **kwargs):
        super(SelectChosen, self).__init__(*args, **kwargs)
        self.attrs = AttributeDict(self.attrs)
        self.attrs.add_class("chosen-select")


class ActionSelect(forms.Select):

    def __init__(self, create_viewname=None, create_original_title=None, list_viewname=None, group_data_label=None, *args, **kwargs):
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


