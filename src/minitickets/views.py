# coding: utf-8

from django.shortcuts import render

from lib.utils.views.base import TemplateSmartView as TemplateView
from lib.utils.views.edit import CreateView, UpdateView, DeleteView
from lib.utils.views.tables import SingleTableView as ListView
from src.minitickets.forms import FuncionarioCreateForm, FuncionarioUpdateForm, ProdutoForm, \
    ClienteUpdateForm, ClienteCreateForm, TicketCreateForm

from src.minitickets.models import Funcionario, Produto, Cliente, Ticket
from src.minitickets.tables import FuncionarioTable, ProdutoTable, ClienteTable


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'


def teste(request):
    return render(request, template_name='teste-modal.html')


# <editor-fold desc="Funcionario">
class FuncionarioCreateView(CreateView):
    model = Funcionario
    form_class = FuncionarioCreateForm


class FuncionarioUpdateView(UpdateView):
    model = Funcionario
    form_class = FuncionarioUpdateForm


class FuncionarioListView(ListView):
    model = Funcionario
    table_class = FuncionarioTable


class FuncionarioDeleteView(DeleteView):
    model = Funcionario
# </editor-fold>


# <editor-fold desc="Cliente">
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteCreateForm


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteUpdateForm


class ClienteListView(ListView):
    model = Cliente
    table_class = ClienteTable


class ClienteDeleteView(DeleteView):
    model = Cliente
# </editor-fold>


# <editor-fold desc="Produto">
class ProdutoCreateView(CreateView):
    model = Produto
    fields = ['nome', 'descricao']
    form_class = ProdutoForm


class ProdutoUpdateView(UpdateView):
    model = Produto


class ProdutoListView(ListView):
    model = Produto
    table_class = ProdutoTable


class ProdutoDeleteView(DeleteView):
    model = Produto
# </editor-fold>


# <editor-fold desc="Ticket">
class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketCreateForm

    def form_invalid(self, form):
        response = super(TicketCreateView, self).form_invalid(form)
        response.status_code = 400
        return response


class TicketListView(ListView):
    model = Ticket
    #table_class = TicketTable


class TicketDeleteView(DeleteView):
    model = Ticket
# </editor-fold>