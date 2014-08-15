# -*- coding: utf-8 -*-

import os

from django import template
from django.conf import settings
from django.forms.util import flatatt
from django.template import TemplateSyntaxError, Node
from django.utils.html import format_html

from ..tags import token_kwargs, resolve_kwargs


register = template.Library()

IMG_TAG = '<img{0} />'
STATIC_URL = getattr(settings, 'STATIC_URL', '/static/')


class ImageNode(Node):
    def __init__(self, image, kwargs=None):
        super(ImageNode, self).__init__()
        self.image = image
        self.kwargs = kwargs or {}

    def render(self, context):
        image = self.image.resolve(context)
        attrs = resolve_kwargs(self.kwargs, context)
        default = attrs.pop('default', None)

        if default:
            default = STATIC_URL + default

        try:
            src = getattr(image, 'url', '') if os.path.exists(getattr(image, 'path', '')) else default
        except ValueError:
            # has no file associated
            src = default

        if not src:
            return ''

        attrs['src'] = src
        return format_html(IMG_TAG, flatatt(attrs))

@register.tag
def image(parser, token):
    """
    Render a HTML icon.

    The tag can be given either a `.Icon` object or a name of the icon.
    An optional second argument can specify the icon prefix to use.
    An optional third argument can specify the icon html tag to use.
    An optional fourth argument can specify the icon content to use.
    Others arguments can specify any html attribute to use.

    Example::
        {% icon 'icon' 'kwarg1'='value1' 'kwarg2'='value2' ... %}
        {% icon 'icon' 'prefix'='fa-' 'kwarg1'='value1' 'kwarg2'='value2' ... %}
        {% icon 'icon' 'prefix'='fa-' 'html_tag'='b' 'kwarg1'='value1' 'kwarg2'='value2' ... %}
        {% icon 'icon' 'prefix'='fa-' 'html_tag'='b' 'content'='R$' 'kwarg1'='value1' 'kwarg2'='value2' ... %}
    """
    bits = token.split_contents()
    try:
        tag, image = bits.pop(0), parser.compile_filter(bits.pop(0))
    except ValueError:
        raise TemplateSyntaxError("'%s' must be given a image." % bits[0])

    kwargs = {}

    # split optional args
    if len(bits):
        kwargs = token_kwargs(bits, parser)

    return ImageNode(image, kwargs=kwargs)