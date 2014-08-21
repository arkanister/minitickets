# coding: utf-8

from django import template
from django.core.urlresolvers import NoReverseMatch
from django.template import TemplateSyntaxError, Node

register = template.Library()


class ActionNode(Node):
    def __init__(self, action, instance, kwargs=None):
        super(ActionNode, self).__init__()
        self.action = action
        self.instance = instance

    def render(self, context):
        action = self.action.resolve(context)
        instance = self.instance.resolve(context)
        user = context['request'].user

        if not user.has_perms(action.perms):
            return ''

        try:
            return action.render(instance)
        except NoReverseMatch:
            return ''


@register.tag('action')
def do_action(parser, token):
    """
    Render a HTML action.
    """
    bits = token.split_contents()
    tag = bits.pop(0)

    try:
        action = parser.compile_filter(bits.pop(0))
        instance = parser.compile_filter(bits.pop(0))
    except ValueError:
        raise TemplateSyntaxError("'%s' must be given a two args." % tag)

    return ActionNode(action, instance)