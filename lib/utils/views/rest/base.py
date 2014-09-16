# coding: utf-8

import re
from django.conf import settings
from django.core.urlresolvers import resolve

from django.db.models import get_model

from rest_framework import exceptions
from rest_framework.views import APIView

from lib.utils.secure import MD5Encrypt


CDKEY_RE = re.compile('([a-zA-Z0-9]{5})-([a-zA-Z0-9]{9})-([a-zA-Z0-9]{5})')
Licence = get_model(*getattr(settings, 'REST_LICENCE_MODEL').split('.'))


class BaseServiceView(APIView):
    log_class = get_model(*getattr(settings, 'REST_LOG_MODEL').split('.'))

    def initial(self, request, *args, **kwargs):
        super(BaseServiceView, self).initial(request, *args, **kwargs)

        # load cdkey and licence
        try:
            cdkey = MD5Encrypt.decrypt(kwargs.get('cdkey'))
        except (ValueError, TypeError):
            raise exceptions.AuthenticationFailed()

        if not bool(CDKEY_RE.match(cdkey)):
            # cdkey in invalid format
            raise exceptions.AuthenticationFailed()

        self.cdkey = cdkey

        # get licence by cdkey
        licence = Licence._default_manager.filter(cdkey__iexact=cdkey)

        if not licence.exists():
            # cdkey not exists
            raise exceptions.AuthenticationFailed()

        self.licence = licence.get()

    def finalize_response(self, request, response, *args, **kwargs):
        self.log_class._default_manager.create(
            licence=getattr(self, 'licence', None),
            status=response.status_code,
            view_name=resolve(request.path_info).url_name
        )
        return super(BaseServiceView, self).finalize_response(request, response, *args, **kwargs)