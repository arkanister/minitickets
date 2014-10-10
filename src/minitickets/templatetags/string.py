from django import template

register = template.Library()


@register.filter(name="lpad")
def do_lpad(obj, length):
    pattern = "%0" + str(length) + "d"
    return pattern % obj