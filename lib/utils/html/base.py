# -*- coding: utf-8 -*-

from django.core.validators import EMPTY_VALUES
from django.utils import six
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.html import escape

EMPTY_STR, BLANK_CHAR = '', ' '


class AttributeDict(dict):
    """
    A wrapper around `dict` that knows how to render itself as HTML
    style tag attributes.

    The returned string is marked safe, so it can be used safely in a template.
    See `.as_html` for a usage example.
    """

    _errors = {
        'invalid_type': "'%s' value is not a %s object",
    }

    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        # get all css classes defined
        self._cached_class = self.get('class', '').split(' ')

    def _update_class(self):
        self['class'] = ' '.join(self._cached_class)

    def add_class(self, name):
        """
        Add a new css class in dict
        :param name: class name to add.
        """
        if not self.has_class(name):
            self._cached_class.append(name)
            self._update_class()

    def remove_class(self, name):
        """
        Remove a css class of the dict
        :param name: class name to remove.
        """
        if self.has_class(name):
            self._cached_class.remove(name)
            self._update_class()

    def has_class(self, name):
        """
        Check if exists class
        :param name: class name to check.
        """
        return name in self._cached_class

    def attr(self, name, value=None):
        """
        A smart method to get and set attr in `AttributeDict`.
        :param name: attribute name.
        :param value: attribute value.
        """
        name = force_str(name)
        if value is None:
            return self.get(name, None)
        elif name == 'class':
            self.add_class(value)
        else:
            self[name] = value

    def has_attr(self, name):
        """
        Check if exists attr
        :param name: class name to check.
        """
        return name in self and not self[name] in EMPTY_VALUES

    def as_html(self):
        """
        Render to HTML tag attributes.

        Example:

        .. code-block:: python

            >>> from lib.utils.html import AttributeDict
            >>> attrs = AttributeDict({'class': 'mytable', 'id': 'someid'})
            >>> attrs.as_html()
            'class="mytable" id="someid"'

        :rtype: `~django.utils.safestring.SafeUnicode` object

        """
        return mark_safe(BLANK_CHAR.join([
            '%s="%s"' % (k, escape(v if not callable(v) else v()))
            for k, v in six.iteritems(self) if not v in EMPTY_VALUES]))

    def __str__(self):
        return self.as_html()

    def __repr__(self):
        return "<AttributeDict: %s>" % str(self)