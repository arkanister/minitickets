# coding: utf-8

from lib.utils.views.base import TemplateSmartView as TemplateView
from src.minitickets.models import Funcionario


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'