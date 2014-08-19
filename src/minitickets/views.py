# coding: utf-8

from django.shortcuts import render
from lib.utils.views.base import TemplateSmartView as TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'


def teste(request):
    return render(request, template_name='teste-modal.html')