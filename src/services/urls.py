# coding: utf-8

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from src.services.views import TestServiceView, TicketServiceView

urlpatterns = patterns('',
    url(r'^test/$', TestServiceView.as_view(), name='test'),

    url(r'tickets/$', csrf_exempt(TicketServiceView.as_view()), name='tickets'),
    url(r'^tickets/(?P<pk>\d+)/$', TicketServiceView.as_view(), name='tickets-detail')

)