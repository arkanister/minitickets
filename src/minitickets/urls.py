# coding: utf-8

from django.conf.urls import patterns, include, url
from src.minitickets.views import CreateFuncionarioView, ListFuncionarioView

urlpatterns = patterns('src.minitickets.views',
    # <editor-fold desc="Funcionário">
    url(r'^funcionario/add/$', CreateFuncionarioView.as_view(), name='add-funcionario'),
    url(r'^funcionarios/$', ListFuncionarioView.as_view(), name='list-funcionario'),
    # </editor-fold>

)