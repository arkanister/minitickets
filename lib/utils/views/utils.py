# -*- coding: utf-8 -*-

import re
import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.utils.html import strip_tags, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ..html import Icon, AttributeDict


class JsonResponse(HttpResponse):
    def __init__(self, context, status=None):
        content_type = mimetype = 'application/json'
        self.context_data = context
        super(JsonResponse, self).__init__('', content_type, status, mimetype)
        self.content = self.convert_context_to_json()

    def convert_context_to_json(self):
        """
        This method serialises a context data and
        returns JSON object with its fields and errors
        """
        return json.dumps(self.context_data)


class Accessor(str):
    """
    A string describing a path from one object to another via attribute/index
    accesses. For convenience, the class has an alias `.A` to allow for more concise code.

    Relations are separated by a ``.`` character.
    """
    SEPARATOR = '__'

    def _bits(self):
        if self == '':
            return ()
        return self.split(Accessor.SEPARATOR)
    bits = property(_bits)

    def resolve(self, instance, quiet=False):
        """
        Return an object described by the accessor by traversing the attributes
        of *context*.

        Example:

        .. code-block:: python

            >>> x = Accessor('__len__')
            >>> x.resolve('brad')
            4
            >>> x = Accessor('0__upper')
            >>> x.resolve('brad')
            'B'

        :type  context: `object`
        :param context: The root/first object to traverse.
        :type     safe: `bool`
        :param    safe: Don't call anything with ``alters_data = True``
        :type    quiet: bool
        :param   quiet: Smother all exceptions and instead return `None`
        :returns: target object
        :raises: anything ``getattr(a, "b")`` raises, e.g. `TypeError`,
                 `AttributeError`, `KeyError`, `ValueError` (unless *quiet* ==
                 `True`)

        `~.Accessor.resolve` attempts lookups in the following order:

        - dictionary (e.g. ``obj[related]``)
        - attribute (e.g. ``obj.related``)
        - list-index lookup (e.g. ``obj[int(related)]``)

        Callable objects are called, and their result is used, before
        proceeding with the resolving.
        """
        try:
            current = instance
            for bit in self.bits:
                try:  # dictionary lookup
                    current = current[bit]
                except (TypeError, AttributeError, KeyError):
                    try:  # attribute lookup
                        current = getattr(current, bit)
                    except (TypeError, AttributeError):
                        try:  # list-index lookup
                            current = current[int(bit)]
                        except (IndexError,  # list index out of range
                                ValueError,  # invalid literal for int()
                                KeyError,    # dict without `int(bit)` key
                                TypeError,   # unsubscriptable object
                                ):
                            raise ValueError('Failed lookup for key [%s] in %r'
                                             ', when resolving the accessor %s'
                                              % (bit, current, self))
                if callable(current):
                    current = current()
                # important that we break in None case, or a relationship
                # spanning across a null-key will raise an exception in the
                # next iteration, instead of defaulting.
                if current is None:
                    break
            return unicode(current)
        except:
            if not quiet:
                raise


class SmartStr(str):
    """
    A string describing a tags from string via patterns accesses.
    For convenience, the class has an alias `.S` to allow for more concise code.
    """

    def compile(self, context=None, prettify=False, quiet=True):
        """
        Copile any tags in string.
        :type    quiet: bool
        :param   quiet: Smother all exceptions and instead return `None`
        :raises: anything
        """
        icon_regex = re.compile(r'\[icon:([a-z\-]+)\]', re.IGNORECASE)  # [icon:some-icon]
        attribute_regex = re.compile(r'\[([a-zA-Z0-9_]+)\]', re.IGNORECASE)  # [name] [product__name] ...

        string = self.decode('utf-8')

        if context is not None:
            for name in set(attribute_regex.findall(string)):
                from django.db.models import Model
                regex = re.compile(r'\[%s\]' % name, re.IGNORECASE)
                if isinstance(context, Model) and name == 'unicode':
                    value = unicode(context)
                elif isinstance(context, Model) and name in ['verbose_name', 'verbose_name_plural']:
                    opts = getattr(context, '_meta')
                    value = getattr(opts, name)
                else:
                    value = Accessor(name).resolve(context, quiet=quiet)
                if value:
                    string = regex.sub(value, string)

        for icon in set(icon_regex.findall(string)):
            regex = re.compile('\[icon:%s\]' % icon, re.IGNORECASE)
            string = regex.sub(Icon(icon.lower()).as_html(), string)

        if prettify:
            words = strip_tags(string.strip()).split(' ')
            for word in words:
                string.replace(word, word.capitalize())

        return string

S = SmartStr


class UrlHelper(object):

    @staticmethod
    def make_by_model(model, view_type, args=[], kwargs={}):
        """
        A maker to generate defaults urls
        the view_type can be 'add', 'edit', 'list', 'delete' or 'detail'
        """
        NAMES = ['add', 'change', 'delete', 'detail', 'list']
        view_type = NAMES[view_type - 1]
        template_view = "{0}:{1}-{2}"
        template_view_short = "{0}-{1}"
        app_label = model._meta.app_label.lower()
        model_name = model._meta.object_name.lower()
        try:
            url_conf = template_view.format(app_label, view_type, model_name)
            return reverse(url_conf, args=args, kwargs=kwargs)
        except:
            # views without namespace
            url_conf = template_view_short.format(view_type, model_name)
            return reverse(url_conf, args=args, kwargs=kwargs)


# <editor-fold desc="Breadcrumbs">
class Breadcrumb(object):
    """
    Breadcrumb can have methods to customize breadcrumb object, Breadcrumbs
    class send to us name and url.
    """

    def __init__(self, name, url=None, icon=None):
        self.name = name
        self.url = url or ''
        self._icon = icon

    def has_icon(self):
        return not self.icon is None

    def _get_icon(self):
        icon = self._icon
        if isinstance(icon, basestring):
            icon = Icon('icon')
        elif not isinstance(icon, Icon):
            return None
        return icon

    icon = property(_get_icon)

    def __str__(self):
        # todo verificar conversão de unicode
        return self.name.encode('utf-8')

    def __repr__(self):
        return u"<Breadcrumb: %s>" % self.name


class BoundBreadcrumbs(object):
    def __init__(self, breadcrumbs, breadcrumb):
        self.breadcrumbs = breadcrumbs
        self.breadcrumb = breadcrumb

    def as_html(self):
        return format_html(
            '<li{1}>{1}{2}</li>',
            '' if not self.breadcrumb == self.breadcrumbs.last else ' ' + AttributeDict(
                {'class': 'active'}).as_html(),
            self.icon.as_html() + ' ',
            self.name
        )

    def as_a(self):
        return format_html(
            '<li{0}><a{1}>{2}{3}</a></li>',
            '' if not self.breadcrumb == self.breadcrumbs.last else ' ' + AttributeDict(
                {'class': 'active'}).as_html(),
            ' ' + AttributeDict({'href': self.url or '#'}).as_html(),
            self.icon.as_html() if self.icon else '',
            self.name
        )


class Breadcrumbs(object):
    _errors = {
        "type_error": _("'%s' object doest not is a %s.")
    }

    def __init__(self):
        self.breadcrumbs = []

    def add(self, name, url=None, icon=None, index=None):
        if isinstance(icon, str):
            icon = Icon(name=icon)
        breadcrumb = Breadcrumb(name, url, icon)
        if index is None:
            self.breadcrumbs.append(breadcrumb)
        else:
            assert isinstance(index, int), self._errors['type_error'] % (type(index).__name__, 'integer')
            self.breadcrumbs.insert(index, breadcrumb)

    def remove(self, index):
        self.breadcrumbs.pop(index)

    def _get_first(self):
        return self.breadcrumbs[0]

    first = property(_get_first)

    def _get_last(self):
        return self.breadcrumbs[-1]

    last = property(_get_last)

    def is_empty(self):
        return len(self.breadcrumbs) == 0

    def __iter__(self):
        for breadcrumb in self.breadcrumbs:
            yield BoundBreadcrumbs(self, breadcrumb)
# </editor-fold>


class Messages(object):

    DEBUG = messages.DEBUG
    INFO = messages.INFO
    SUCCESS = messages.SUCCESS
    WARNING = messages.WARNING
    ERROR = messages.ERROR

    DEFAULT_TAGS = messages.DEFAULT_TAGS

    _errors = {
        "type_error": _("'%s' object doest not is a %s.")
    }

    def __init__(self, request):
        self.request = request

    def success(self, message, extra_tags='alert-success'):
        """
        Add a success message in request
        :param message: content of message
        :param extra_tags: tags of message
        """
        messages.success(self.request, mark_safe(message), extra_tags=extra_tags)

    def info(self, message, extra_tags='alert-info'):
        """
        Add a info message in request
        :param message: content of message
        :param extra_tags: tags of message
        """
        messages.info(self.request, mark_safe(message), extra_tags=extra_tags)

    def error(self, message, extra_tags='alert-danger'):
        """
        Add a danger message in request
        :param message: content of message
        :param extra_tags: tags of message
        """
        messages.error(self.request, mark_safe(message), extra_tags=extra_tags)

    def debug(self, message, extra_tags='alert-warning'):
        """
        Add a debug message in request
        :param message: content of message
        :param extra_tags: tags of message
        """
        messages.debug(self.request, mark_safe(message), extra_tags=extra_tags)

    def warning(self, message, extra_tags='alert-warning'):
        """
        Add a warning message in request
        :param message: content of message
        :param extra_tags: tags of message
        """
        messages.warning(self.request, mark_safe(message), extra_tags=extra_tags)

    def remove(self, index):
        assert isinstance(index, int), self._errors['type_error'] % (type(index).__name__, 'integer')
        self.request._messages.remove(index)

    def __repr__(self):
        return '<MessageRequestAdapter>'


class TableAction(object):

    def __init__(self, viewname, verbose_name=None, icon=None, args=None, kwargs=None, perms=None, attrs=None):
        self.viewname = viewname
        self._icon = icon
        self.verbose_name = verbose_name
        self.args = args or []
        self.kwargs = kwargs or {}
        self.perms = perms or []
        self.attrs = AttributeDict(attrs or {})

    def _get_icon(self):
        icon = self._icon
        if isinstance(icon, basestring):
            icon = Icon(icon)
        elif not isinstance(icon, Icon):
            return None
        return icon
    icon = property(_get_icon)

    def has_icon(self):
        return not self.icon == None


class TableActions(object):

    _errors = {
        "type_error": _("'%s' object doest not is a %s.")
    }

    def __init__(self):
        self.actions = []

    def add(self, viewname, verbose_name=None, icon=None, args=None, kwargs=None, perms=None, attrs=None, index=None):
        action = TableAction(
            viewname, verbose_name=verbose_name,
            icon=icon, args=args, kwargs=kwargs,
            perms=perms, attrs=attrs
        )
        if index is None:
            self.actions.append(action)
        else:
            assert isinstance(index, int), self._errors['type_error'] % (type(index).__name__, 'integer')
            self.actions.insert(index, action)

    def remove(self, index):
        self.actions.remove(index)

    def __iter__(self):
        for action in self.actions:
            yield action