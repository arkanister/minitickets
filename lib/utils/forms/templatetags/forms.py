# -*- coding: utf-8 -*-

from django import template
from django.template import TemplateSyntaxError, Node, loader

from ...html import AttributeDict
from ...html.templatetags import token_kwargs, resolve_kwargs


register = template.Library()


class InputNode(Node):

    def __init__(self, field, attrs=None, kwargs=None):
        super(InputNode, self).__init__()
        self.field = field
        self.kwargs = kwargs or None
        self.attrs = attrs or {}

    def render(self, context):
        field = self.field.resolve(context)
        kwargs = resolve_kwargs(self.kwargs, context)
        attrs = AttributeDict(resolve_kwargs(self.attrs, context))

        # merge attrs
        for key, value in field.field.widget.attrs.items():
            attrs.attr(key, value)

        field.field.widget.attrs = attrs

        template = loader.get_template(kwargs.pop('template', 'forms/input.html'))

        kwargs.update({'field': field})
        context = loader.Context(kwargs)
        return template.render(context)


@register.tag
def input(parser, token):
    """
    Render a HTML icon.

    The tag can be given either a `.Icon` object or a name of the icon.
    An optional second argument can specify the template name to use.
    An optional argument define a html attrs to field widget
    Others arguments can specify any settings to use in template.

    Example::
        {% input field kwarg1=value1 kwarg2=value2 ... %}
        {% input field 'template'='any-template.html' kwarg1=value1 kwarg2=value2 ... %}
        {% input field 'template'='any-template.html' kwarg1=value1 kwarg2=value2 ... attrs attr1=value1 attr2=value2 ... %}
    """
    bits = token.split_contents()
    try:
        tag, _field = bits.pop(0), parser.compile_filter(bits.pop(0))
    except ValueError:
        raise TemplateSyntaxError("'%s' must be given a field." % bits[0])

    kwargs = {}
    attrs = {}

    # split optional args
    if len(bits) > 0:
        kwargs = token_kwargs(bits, parser)

    if len(bits) > 0 and bits[0] == 'attrs':
        attrs = token_kwargs(bits[1:], parser)

    return InputNode(_field, attrs=attrs, kwargs=kwargs)