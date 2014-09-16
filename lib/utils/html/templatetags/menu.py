# -*- coding: utf-8 -*-

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.template import Node
from django.utils.safestring import mark_safe
from ..menu.base import menu_factory

from src.conf.menu import MAIN_NAV


register = template.Library()


context_processor_error_msg = (
    "{%% %s %%} requires django.core.context_processors.request "
    "to be in your settings.TEMPLATE_CONTEXT_PROCESSORS in order for "
    "the included template tags to function correctly."
)


class RenderMenuNode(Node):
    """
    :param    user: the user to render menu
    :type     user: User object
    :param    path: path of the request
    :type     path: str
    """

    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured(context_processor_error_msg % 'menu')
        request = context['request']
        return mark_safe(u''.join(
            [m.as_html() for m in menu_factory(MAIN_NAV, request)]
        ))


@register.tag('menu')
def do_menu(parser, token):
    """
    Render a HTML field.

    The tag can be given either a `User` and `path` values.

    Example::

        {% menu %}
    """
    bits = token.split_contents()
    return RenderMenuNode()