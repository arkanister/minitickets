# coding: utf-8

from lib.utils.views.base import TemplateSmartView as TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
    title = 'Bem Vindo!'
    subtitle = 'MiniTickets'