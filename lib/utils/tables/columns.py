# -*- coding: utf-8 -*-

from django.template import loader
from django.utils import formats
from django.utils.text import Truncator

import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ..html import AttributeDict, Icon


def merge_attrs(base_attrs, attrs):
    """
    Merge attrs based in attribute dict.
    """
    td = AttributeDict(base_attrs.get('td', {}))
    th = AttributeDict(base_attrs.get('th', {}))

    # merge td
    for key, value in attrs.get('td', {}).items():
        td.attr(key, value)

    # merge th
    for key, value in attrs.get('th', {}).items():
        th.attr(key, value)

    return {'td': td, 'th': th}


class CheckBoxColumn(tables.CheckBoxColumn):

    BASE_ATTRS = {
        'th': {"width": "40px"},
        'td': {"class": "center"}
    }

    def __init__(self, attrs=None, orderable=False, **extra):
        attrs = merge_attrs(CheckBoxColumn.BASE_ATTRS, attrs or {})
        super(CheckBoxColumn, self).__init__(attrs=attrs, orderable=orderable, **extra)

    @property
    def header(self):
        default = {'type': 'checkbox'}
        general = self.attrs.get('input')
        specific = self.attrs.get('th__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs.update({"class": "ace"})
        return mark_safe('<label><input %s/><span class="lbl"></span></label>' % attrs.as_html())

    def render(self, value, bound_column):
        default = {
            'type': 'checkbox',
            'name': bound_column.name,
            'value': value
        }
        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs.update({"class": "ace", "data-toggle": "checkbox"})
        return mark_safe('<label><input %s/><span class="lbl"></span></label>' % attrs.as_html())


class BooleanColumn(tables.BooleanColumn):

    BASE_ATTRS = {'th': {'width': '100px'}, 'td': {'class': 'center'}}
    DEFAULT_ICONS = ['check-circle', 'times-circle']

    def __init__(self, null=False, attrs=None, orderable=False, **kwargs):
        attrs = merge_attrs(BooleanColumn.BASE_ATTRS, attrs or {})
        super(BooleanColumn, self).__init__(null=null, attrs=attrs, orderable=orderable, **kwargs)

    def get_icon(self, value):
        index = int(not value)
        text = self.yesno[index]
        text = BooleanColumn.DEFAULT_ICONS[index] if text in (u'✔', u'✘', None, '') else text
        attrs = AttributeDict({'class': 'bigger-130 ace-icon'})
        attrs.add_class('green' if value else 'red')
        return Icon(text, attrs=attrs)

    def render(self, value, record, bound_column):
        icon = self.get_icon(value)
        return icon.as_html()


class IntegerColumn(tables.Column):

    def __init__(self, format="%d", *args, **kwargs):
        self.format = format
        super(IntegerColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return self.format % int(value)


class IdColumn(IntegerColumn):

    BASE_ATTRS = {"th": {"width": "100px"}, "td": {"class": "center"}}

    def __init__(self, verbose_name=_("Code"), format="%05d", attrs=None, *args, **kwargs):
        attrs = merge_attrs(IdColumn.BASE_ATTRS, attrs or {})
        super(IdColumn, self).__init__(verbose_name=verbose_name, format=format, attrs=attrs, *args, **kwargs)


class ChoiceColumn(tables.Column):

    def __init__(self, conf, *args, **kwargs):
        super(ChoiceColumn, self).__init__(*args, **kwargs)
        self._conf = conf

    def _get_conf(self):
        conf = {}
        for key, value in self._conf.items():
            attrs = AttributeDict()
            conf[key] = {}

            for k, v in value.items():
                if k == 'icon':
                    icon = Icon(v) if isinstance(v, basestring) else v
                    conf[key][k] = icon.as_html()
                elif k == 'color':
                    attrs.add_class(v)
                else:
                    attrs.attr(k, v)

            conf[key]['attrs'] = attrs

        return conf
    conf = property(_get_conf)

    def render(self, value, record, bound_column):
        v = getattr(record, bound_column.accessor)
        conf = self.conf.get(v, None)

        # add a tip text
        attrs = conf.get('attrs', AttributeDict())
        attrs.add_class('tip')
        attrs.attr('title', value)

        template = loader.get_template_from_string("<span {{ attrs }}>{{ value }}</span>")
        return template.render(loader.Context({
            'value': conf.get('icon', None) or value,
            'attrs': attrs.as_html()
        }))


class CheckBoxColumn(tables.CheckBoxColumn):

    def __init__(self, attrs=None, accessor=tables.A("pk"), orderable=False, **extra):
        attrs = attrs or {}
        attrs.update({
            "th": {"width": "40px", "class": "center"},
            "td": {"class": "center"}
        })
        super(CheckBoxColumn, self).__init__(attrs=attrs, accessor=accessor, orderable=False, **extra)

    @property
    def header(self):
        default = {'type': 'checkbox'}
        general = self.attrs.get('input')
        specific = self.attrs.get('th__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs.update({"class": "ace"})
        return mark_safe('<label><input %s/><span class="lbl"></span></label>' % attrs.as_html())

    def render(self, value, bound_column): # pylint: disable=W0221
        default = {
            'type': 'checkbox',
            'name': bound_column.name,
            'value': value
        }
        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(default, **(specific or general or {}))
        attrs.update({"class": "ace", "data-toggle": "checkbox"})
        return mark_safe('<label><input %s/><span class="lbl"></span></label>' % attrs.as_html())


class LinkColunmWithPerm(tables.LinkColumn):

    def __init__(self, perm_name, *args, **kwargs):
        self.perm_name = perm_name
        kwargs["args"] = kwargs.get("args", None) or [tables.A("pk")] # url args
        return super(LinkColunmWithPerm, self).__init__(*args, **kwargs)

    def render(self, value, record, bound_column):
        if self.perm_name == "":
            return value
        else:
            return super(LinkColunmWithPerm, self).render(value, record, bound_column)


class CurrencyColumn(tables.Column):

    def render(self, value):
        return formats.number_format(value, decimal_pos=2)


class TruncateCharsColumn(tables.Column):

    def __init__(self, length=30, *args, **kwargs):
        self.length = length
        super(TruncateCharsColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return Truncator(value).chars(self.length)


class TruncateWordsColumn(tables.Column):

    def __init__(self, words=5, *args, **kwargs):
        self.words = words
        super(TruncateWordsColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return Truncator(value).words(self.words, truncate=' ...')