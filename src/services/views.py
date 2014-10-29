# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from lib.utils.views.rest.base import View as ServiceView

from src.minitickets.models import Ticket
from src.services.serializers import TicketSerializer, TicketCreateSerializer


# Test With:
#    AccessToken u'G7WEBRRCU&1'
#    MD5: bis+eVFKK5xipGK4+fzxOw==
#    MD5 Uri: bis+eVFKK5xipGK4+fzxOw==/tickets/
#    TODO: make a test


class TestServiceView(ServiceView):

    def get(self, request, *args, **kwargs):
        return Response({
            'status': 'ok'
        })


class TicketServiceView(ServiceView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        tikect_id = kwargs.get("pk")
        serializer_kwargs = {}

        if tikect_id is not None:
            serializer_kwargs['instance'] = get_object_or_404(self.model, pk=tikect_id)
        else:
            serializer_kwargs['many'] = True
            serializer_kwargs['instance'] = Ticket.objects.filter(
                cliente=self.client.pk, produto=self.product.pk)

        serializer = TicketSerializer(**serializer_kwargs)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # prepare data
        data = dict([(key, value) for key, value in request.POST.items()])
        data['cliente'] = self.client.pk
        data['produto'] = self.product.pk

        serialize = TicketCreateSerializer(data=data)

        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=201)
        return Response(serialize.errors, status=400)