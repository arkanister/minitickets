# -*- coding: utf-8 -*-

import re
import urllib
import hashlib
import httplib

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import EMPTY_VALUES
from django.template import Node
from django.template.base import TemplateSyntaxError
from django.template.defaultfilters import safe
from django.conf import settings
from django.utils import formats
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.http import urlencode

from ..tags import token_kwargs
from ...decorators import deprecated


context_processor_error_msg = (
    "{%% %s %%} requires django.core.context_processors.request "
    "to be in your settings.TEMPLATE_CONTEXT_PROCESSORS in order for "
    "the included template tags to function correctly."
)


register = template.Library()


@register.filter(name="image")
def image(obj, blank="image.png"):
    blank, value = settings.STATIC_URL + blank, None
    if hasattr(obj, "url"):
        value = obj.url
    elif obj is not None:
        value = force_text(obj)
    return value or blank


@register.filter(name="currency")
def currency(value):
    return formats.number_format(value, decimal_pos=2)


@register.filter(name="get_from_object")
def get_from_object(field, attr=None):
    return field.field.queryset.get(pk=field.value())


@register.filter(name="has_perm")
def has_perm(user, perm):
    return user.has_perm(perm) if user is not None else False


@register.filter(name="has_perms")
def has_perms(user, perms):
    perms = perms.split(",")
    return user.has_perms(perms) if user is not None else False


@register.filter(name="has_some_perms")
def has_some_perms(user, perms):
    perms = perms.split(",")
    if user is not None:
        for perm in perms:
            if user.has_perm(perm):
                return True
    return False


@deprecated
@register.filter(name="add_left_zeros")
def add_left_zeros(obj, value):
    if obj is None or obj == "":
        return ""
    pattern = "%0"+str(value)+"d"
    return pattern % obj


@register.filter(name='lpad')
def lpad(obj, size):

    if isinstance(obj, basestring):
        try:
            obj = int(obj)
        except Exception:
            return ''

    if obj in EMPTY_VALUES:
        return ''

    pattern = '%{0}{1}d'.format('0', size)
    return pattern % obj


@register.filter(name="split")
def split(obj, arg):
    """
    Uses to split on template.
    """
    if type(obj) in (list, tuple):
        return obj.split(arg)
    return ''


@register.filter(name="join")
def join(obj, arg):
    """
    Uses to join on template.
    """
    if type(obj) in (list, tuple):
        return arg.join(obj)
    return ''


@register.filter(name="errors")
def errors(field, attrs={}):
    """ Uses to get a field errors """
    template_errors = u'<div class="help-block">{0}</div>'
    template_error = u'<p>{0}</p>'
    if field.errors:
        errors = [template_error.format(error) for error in field.errors]
        return safe(template_errors.format("".join(errors)))
    return ""


@register.filter(name="valueorchar")
def valueorchar(value, char=""):
    """ to get a char in none values """
    return value or char


@register.filter(name="is_active_page")
def is_active_page(request, pattern):
    """
    Uses to check if pattern is of active page.
    """
    if re.search(pattern, request.path):
        return True
    return False


@register.simple_tag
def active_page_class(request, pattern, class_name="active"):
    """
    Uses to get active class for a main nav.
    """
    if re.search(pattern, request.path):
        return class_name
    return ''


GRAVATAR_DOMAIN = "gravatar.com"
GRAVATAR_PATH = "/avatar/"


@register.filter(name="show_gravatar_url")
def show_gravatar_url(email, size=48):
    """ Uses to get correct url to gravatar email. """
    if not email is None:
        query = urllib.urlencode({
            'gravatar_id': hashlib.md5(email).hexdigest(),
            'size': str(size),
            'default': '/'
        })
        full_path = "%s?%s" % (GRAVATAR_PATH, query)
    
        # Create connection and test for 302 redirect
        conn = httplib.HTTPConnection(GRAVATAR_DOMAIN)
        conn.request('HEAD', full_path)
        response = conn.getresponse()
    
        if not response.status == 302:
            return "http://%s%s" % (GRAVATAR_DOMAIN, full_path)
    return "%s%s" % (settings.STATIC_URL, "/images/avatar.png")


class QuerystringNode(Node):
    def __init__(self, updates, removals):
        super(QuerystringNode, self).__init__()
        self.updates = updates
        self.removals = removals

    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured(context_processor_error_msg
                                       % 'querystring')
        params = dict(context['request'].GET)
        for key, value in self.updates.items():
            key = key.resolve(context)
            value = value.resolve(context)
            if key not in ("", None):
                params[key] = value
        for removal in self.removals:
            params.pop(removal.resolve(context), None)
        return escape("?" + urlencode(params, doseq=True))


# {% querystring "name"="abc" "age"=15 %}
@register.tag
def querystring(parser, token):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Brad``)::

        {% querystring "name"="Ayers" "age"=20 %}
        ?name=Ayers&gender=male&age=20
        {% querystring "name"="Ayers" without "gender" %}
        ?name=Ayers

    """
    bits = token.split_contents()
    tag = bits.pop(0)
    updates = token_kwargs(bits, parser)
    # ``bits`` should now be empty of a=b pairs, it should either be empty, or
    # have ``without`` arguments.
    if bits and bits.pop(0) != "without":
        raise TemplateSyntaxError("Malformed arguments to '%s'" % tag)
    removals = [parser.compile_filter(bit) for bit in bits]
    return QuerystringNode(updates, removals)