# coding: utf-8

import re

from django.utils.http import int_to_base36, base36_to_int

from rest_framework import exceptions
from rest_framework.views import APIView

from lib.utils.secure import MD5Encrypt

from src.minitickets.models import Cliente, Produto


class AccessToken(object):

    @staticmethod
    def _parse_cnpj(cpnj):
        cdkey = str(base36_to_int(cpnj))
        return '%2s.%3s.%2s/%4s-%2s' % (
            cdkey[:2],
            cdkey[2:5],
            cdkey[5:8],
            cdkey[8:12],
            cdkey[12:14]
        )

    @staticmethod
    def make(cnpj, product_id):
        return (
            int_to_base36(int(''.join(re.findall(r"\d+", cnpj)))) +
            '&' + str(product_id)
        ).upper()

    @staticmethod
    def get_client_from_access_token(access_token):
        try:
            return Cliente.objects.get(cnpj=AccessToken._parse_cnpj(access_token.split('&')[0]))
        except Cliente.DoesNotExist:
            return None

    @staticmethod
    def get_product_from_access_token(access_token):
        try:
            return Produto.objects.get(pk=int(access_token.split('&')[1]))
        except Produto.DoesNotExist:
            return False


ACCESS_TOKEN_RE = re.compile(r'^([a-zA-Z0-9]{9})&(\d+)')


class View(APIView):

    def initial(self, request, *args, **kwargs):
        # load cdkey and licence
        try:
            access_token = MD5Encrypt.decrypt(kwargs.get('accesstoken').replace('==bar==', '/'))
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed()

        if not bool(ACCESS_TOKEN_RE.match(access_token)):
            # cdkey in invalid format
            raise exceptions.AuthenticationFailed()

        self.client = AccessToken.get_client_from_access_token(access_token)
        self.product = AccessToken.get_product_from_access_token(access_token)

        if not self.client or not self.product:
            raise exceptions.AuthenticationFailed()

        super(View, self).initial(request, *args, **kwargs)
