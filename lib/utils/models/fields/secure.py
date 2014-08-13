# -*- coding: utf-8 -*-

from lib.utils import MD5Encrypt
from django.utils.functional import curry
from django.db import models

class Md5FieldMixin(object):

    """ A MD5 field to encript and decript """

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = MD5Encrypt.encrypt(self.get_prep_value(value))
        return value

    def contribute_to_class(self, cls, name):
        super(Md5FieldMixin, self).contribute_to_class(cls, name)

        def get_FIELD_decrypted(self, field):
            field.value_from_object(self)
            return field.value_from_object(self)

        setattr(cls, 'get_%s_decrypted' % self.name,
                curry(get_FIELD_decrypted, field=self))

    def value_from_object(self, obj):
        """
        Returns the value of this field in the given model instance.
        """
        return MD5Encrypt.decrypt(getattr(obj, self.attname))


class Md5CharField(Md5FieldMixin, models.CharField):
    """ resolve MD5 encrypt/decrypt to CharField """