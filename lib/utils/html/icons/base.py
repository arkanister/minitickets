# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import loader
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

from ..base import AttributeDict


class Icon(object):
    """
    A wrapper around `icon` that knows how to render icon tag.

    The returned string is marked safe, so it can be used safely in a template.
    See `.as_html` for a usage example.
    """

    def __init__(self, name, prefix=None, html_tag=None, content=None, attrs=None):
        self.name = name
        self.prefix = prefix or getattr(settings, "ICON_PREFIX", "icon-")
        self.html_tag = force_str(html_tag or 'i')
        self.content = content or ''

        # load base attrs
        if name:
            self.attrs = AttributeDict(getattr(settings, 'ICON_BASE_ATTRS', {}))

            for key, value in (attrs or {}).items():
                self.attrs.attr(key, value)
        else:
            self.attrs = AttributeDict(attrs or {})

        icon_class = self._get_icon_class()
        if icon_class:
            self.attrs.add_class(icon_class)

    def __repr__(self):
        return "<Icon: %s>" % self.name

    def __str__(self):
        return self.as_html()

    def _get_icon_class(self):
        """ Make the icon class. """
        if self.name is not None:
            return force_str(self.prefix) + force_str(self.name)
        return

    @staticmethod
    def get_template():
        return "<{{ tag_name }} {{ attrs.as_html }}>{{ content }}</{{ tag_name }}>"

    def get_context_data(self):
        return {
            "tag_name": self.html_tag,
            "attrs": self.attrs,
            "content": self.content
        }

    def as_html(self):
        """ Render item tag. """
        template = loader.get_template_from_string(Icon.get_template())
        context = loader.Context(self.get_context_data())
        return mark_safe(template.render(context))