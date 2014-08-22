# coding: utf-8

from django.conf.urls import patterns, url

from src.minitickets.views import FuncionarioCreateView, FuncionarioUpdateView,\
    FuncionarioListView, FuncionarioDeleteView

urlpatterns = patterns('src.minitickets.views',
    # <editor-fold desc="Funcionário">
    url(r'funcionario/add/$', FuncionarioCreateView.as_view(), name='add-funcionario'),
    url(r'funcionario/change/(?P<pk>\d+)/$', FuncionarioUpdateView.as_view(), name='change-funcionario'),
    url(r'funcionarios/$', FuncionarioListView.as_view(), name='list-funcionario'),
    url(r'funcionario/delete/(?P<pk>\d+)/$', FuncionarioDeleteView.as_view(), name='delete-funcionario'),
    # </editor-fold>
)