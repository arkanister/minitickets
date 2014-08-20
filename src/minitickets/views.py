# coding: utf-8

from django.shortcuts import render

from lib.utils.views.base import TemplateSmartView as TemplateView
from lib.utils.views.edit import CreateView
from lib.utils.views.tables import SingleTableView as ListView
from src.minitickets.forms import FuncionarioCreateForm

from src.minitickets.models import Funcionario


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'


def teste(request):
    return render(request, template_name='teste-modal.html')


# <editor-fold desc="Funcionario">
class CreateFuncionarioView(CreateView):
    model = Funcionario
    form_class = FuncionarioCreateForm


class ListFuncionarioView(ListView):
    model = Funcionario
# </editor-fold>