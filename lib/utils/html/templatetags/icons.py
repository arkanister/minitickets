# -*- coding: utf-8 -*-

from django import template
from django.template import TemplateSyntaxError, Node

from ..icons.base import Icon
from ..tags import token_kwargs, resolve_kwargs


register = template.Library()


class IconNode(Node):
    def __init__(self, _icon, kwargs=None):
        super(IconNode, self).__init__()
        self.icon = _icon
        self.kwargs = kwargs or {}

    def render(self, context):
        icon = self.icon.resolve(context)

        if isinstance(icon, Icon):
            return icon.as_html()

        attrs = resolve_kwargs(self.kwargs, context)
        prefix = attrs.pop('prefix', None)
        content = attrs.pop('content', None)
        html_tag = attrs.pop('html_tag', None)

        icon = Icon(icon, prefix=prefix, content=content,
                    html_tag=html_tag, attrs=attrs)

        return icon.as_html()


@register.tag
def icon(parser, token):
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
        tag, _icon = bits.pop(0), parser.compile_filter(bits.pop(0))
    except ValueError:
        raise TemplateSyntaxError("'%s' must be given a icon." % bits[0])

    kwargs = {}

    # split optional args
    if len(bits):
        kwargs = token_kwargs(bits, parser)

    return IconNode(_icon, kwargs=kwargs)