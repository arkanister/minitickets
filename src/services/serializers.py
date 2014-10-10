# coding: utf-8
from rest_framework import serializers
from src.minitickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ('id', 'titulo', 'descricao', 'solucao', 'tipo',
                  'situacao', 'data_abertura', 'data_fechamento')


class TicketCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ('cliente', 'produto', 'titulo', 'descricao', 'tipo')