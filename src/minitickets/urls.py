# coding: utf-8

from django.conf.urls import patterns, url

from src.minitickets.views import FuncionarioCreateView, FuncionarioUpdateView,\
    FuncionarioListView, FuncionarioDeleteView, ProdutoCreateView, ProdutoUpdateView, ProdutoDeleteView, ProdutoListView, \
    ClienteListView, ClienteUpdateView, ClienteDeleteView, ClienteCreateView, TicketCreateView, TicketUpdateView, \
    TicketListView, TicketDeleteView

urlpatterns = patterns('src.minitickets.views',
    # <editor-fold desc="Funcionário">
    url(r'funcionario/add/$', FuncionarioCreateView.as_view(), name='add-funcionario'),
    url(r'funcionario/change/(?P<pk>\d+)/$', FuncionarioUpdateView.as_view(), name='change-funcionario'),
    url(r'funcionarios/$', FuncionarioListView.as_view(), name='list-funcionario'),
    url(r'funcionario/delete/(?P<pk>\d+)/$', FuncionarioDeleteView.as_view(), name='delete-funcionario'),
    # </editor-fold>

    # <editor-fold desc="Produto">
    url(r'produto/add/$',ProdutoCreateView.as_view(), name='add-produto'),
    url(r'produto/change/(?P<pk>\d+)/$',ProdutoUpdateView.as_view(), name='change-produto'),
    url(r'produtos/$',ProdutoListView.as_view(), name='list-produto'),
    url(r'produto/delete/(?P<pk>\d+)/$',ProdutoDeleteView.as_view(), name='delete-produto'),
    # </editor-fold>


    # <editor-fold desc="Cliente">
    url(r'cliente/add/$',ClienteCreateView.as_view(), name='add-cliente'),
    url(r'cliente/change/(?P<pk>\d+)/$',ClienteUpdateView.as_view(), name='change-cliente'),
    url(r'clientes/$',ClienteListView.as_view(), name='list-cliente'),
    url(r'cliente/delete/(?P<pk>\d+)/$',ClienteDeleteView.as_view(), name='delete-cliente'),
    # </editor-fold>

     # <editor-fold desc="Ticket">
    url(r'ticket/add/$',TicketCreateView.as_view(), name='add-ticket'),
    url(r'ticket/change/(?P<pk>\d+)/$',TicketUpdateView.as_view(), name='change-ticket'),
    url(r'tickets/$',TicketListView.as_view(), name='list-ticket'),
    url(r'ticket/delete/(?P<pk>\d+)/$',TicketDeleteView.as_view(), name='delete-ticket'),
    # </editor-fold>
)