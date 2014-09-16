# -*- coding: utf-8 -*-

from django.views.generic.detail import SingleObjectMixin,\
    SingleObjectTemplateResponseMixin

from .base import SmartView as View
from .utils import UrlHelper
from .types import DETAIL, LIST


class BaseDetailView(SingleObjectMixin, View):
    """
    A base view for displaying a single object
    """

    _TYPE = DETAIL

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class DetailView(SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    Render a "detail" view of an object.

    By default this is a model instance looked up from `self.queryset`, but the
    view will support display of *any* object by overriding `self.get_object()`.
    """
    template_name_suffix = '_detail'

    def get_breadcrumbs(self):
        breadcrumbs = super(DetailView, self).get_breadcrumbs()
        name = self.model._meta.verbose_name_plural
        breadcrumbs.add(name, index=-1, url=UrlHelper.make_by_model(self.model, LIST))
        return breadcrumbs

    def get_template_names(self):
        """
        Define a generic template to template name list.
        """
        templates = super(DetailView, self).get_template_names()
        templates.append("forms/detail.html")
        return templates