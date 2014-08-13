# -*- coding: utf-8 -*-

import re

kwarg_re = re.compile(r"(?:(.+)=)?(.+)")


def token_kwargs(bits, parser):
    """
    Based on Django's `~django.template.defaulttags.token_kwargs`, but with a
    few changes:

    - No legacy mode.
    - Both keys and values are compiled as a filter
    """
    kwargs = {}
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match.group(1):
            return kwargs
        key, value = match.groups()
        del bits[:1]
        kwargs[parser.compile_filter(key)] = parser.compile_filter(value)
    return kwargs


def resolve_kwargs(values, context):
    kwargs = {}
    for key, value in values.items():
        key = key.resolve(context)
        value = value.resolve(context)
        if key not in ('', None):
            kwargs[key] = value
    return kwargs