# coding: utf-8

from django.conf.urls import patterns, include, url

# from django.contrib import admin
from django.contrib.auth.views import login, logout
from src.minitickets.forms import AuthenticationForm
from src.minitickets.views import HomeView

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'login/$', login, name='login', kwargs={'authentication_form': AuthenticationForm}),
    url(r'logout/$', logout, name='logout'),
)
