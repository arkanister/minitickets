# coding: utf-8

from django.conf.urls import patterns, url

from src.minitickets.views import FuncionarioCreateView, FuncionarioUpdateView,\
    FuncionarioListView, FuncionarioDeleteView, ProdutoCreateView, ProdutoUpdateView, ProdutoDeleteView, ProdutoListView, \
    ClienteListView, ClienteUpdateView, ClienteDeleteView, ClienteCreateView, TicketCreateView, \
    TicketListView, ClienteAutoCompleteView, TicketDetailView, TicketDesenvolvedorUpdateView, TicketTipoUpdateView, \
    HistoricoTicketCreateView, TempoTicketCreateView, TempoTicketPauseView

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
    url(r'cliente/autocomplete/$',ClienteAutoCompleteView.as_view(), name='autocomplete-cliente'),
    # </editor-fold>

     # <editor-fold desc="Ticket">
    url(r'ticket/add/$', TicketCreateView.as_view(), name='add-ticket'),
    url(r'tickets/$',TicketListView.as_view(), name='list-ticket'),
    url(r'ticket/detail/(?P<pk>\d+)/$',TicketDetailView.as_view(), name='detail-ticket'),
    url(r'tickets/change/desenvolvedor/(?P<pk>\d+)/$',TicketDesenvolvedorUpdateView.as_view(), name='change-desenvolvedor-ticket'),
    url(r'tickets/change/tipo/(?P<pk>\d+)/$',TicketTipoUpdateView.as_view(), name='change-tipo-ticket'),
    # </editor-fold>
    
    # <editor-fold desc="HistoryTicket">
    url(r'history/ticket/add/(?P<ticket>\d+)/$', HistoricoTicketCreateView.as_view(), name='add-historicoticket'),
    # </editor-fold>

    # <editor-fold desc="TimeTicket">
    url(r'time/ticket/add/(?P<ticket>\d+)/$', TempoTicketCreateView.as_view(), name='add-tempoticket'),
    url(r'time/ticket/pause/(?P<ticket>\d+)/$', TempoTicketPauseView.as_view(), name='pause-tempoticket'),
    # </editor-fold>



)