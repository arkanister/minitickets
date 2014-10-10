# -*- coding: utf-8 -*-

import hashlib
from pyDes import triple_des, ECB, PAD_PKCS5
from base64 import b64decode


class MD5Encrypt(object):

    """ A class to encrypt and decrypt string in MD5 """

    DEFAULT_HASH = "xzDwHGMicvBnmH4Qa@oN="

    @classmethod
    def encrypt(cls, value):
        value = str(value)
        _md5 = hashlib.md5()
        _md5.update(cls.DEFAULT_HASH)
        k = triple_des(_md5.digest(), ECB, padmode=PAD_PKCS5)
        return k.encrypt(value).encode("base64").rstrip()

    @classmethod
    def decrypt(cls, value):
        value = b64decode(value)
        _md5 = hashlib.md5()
        _md5.update(cls.DEFAULT_HASH)
        k = triple_des(_md5.digest(), ECB, padmode=PAD_PKCS5)
        return k.decrypt(value)