# -*- coding: utf-8 -*-

import unicodedata

from django.db import models
from django.utils.encoding import force_str


def att_name(name):
    """ uses to normalize the choice atribute name """
    name = force_str(name)
    name = unicodedata.normalize('NFKD', unicode(name))
    return name.decode('utf-8')


class IntegerChoiceField(models.IntegerField):

    def contribute_to_class(self, cls, name):

        super(IntegerChoiceField, self).contribute_to_class(cls, name)

        if not hasattr(self, "_choices_to_attrs"):
            self._get_choices()

        for attr_name, value in self._choices_to_attrs.items():
            setattr(cls, '%s_%s' % (name.upper(), attr_name.upper()), value)

    def _get_choices(self):
        """
        exemple choices:
        simple: ((1, "foo"), (2, "bar"))
        named attr: ((1, (u"foo", "FOO")), (2, ("bar", "BAR")))
        """
        if not hasattr(self, "_choices_to_attrs"):
            choices = []
            choices_to_attrs = []
            for value, name in self.choices:
                if isinstance(name, list) or isinstance(name, tuple):
                    name, attr_name = name
                elif isinstance(name, basestring):
                    attr_name = name
                attr_name = att_name(attr_name)
                choices.append((value, name))
                choices_to_attrs.append((attr_name, value))
            self._choices = tuple(choices)
            self._choices_to_attrs = dict(choices_to_attrs)
        return super(IntegerChoiceField, self)._get_choices()