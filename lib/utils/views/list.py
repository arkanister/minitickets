# -*- coding: utf-8 -*-
from django.core.urlresolvers import NoReverseMatch

from django.views.generic.list import MultipleObjectMixin,\
    MultipleObjectTemplateResponseMixin
from django.http.response import Http404
from django.utils.translation import ugettext as _
from .base import SmartView as View
from .utils import UrlHelper

from .types import LIST, CREATE


class BaseListView(MultipleObjectMixin, View):
    """
    A base view for displaying a list of objects.
    """
    _TYPE = LIST

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)


class ListView(MultipleObjectTemplateResponseMixin, BaseListView):
    """
    Render some list of objects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
    pluralize_title = True

    def get_template_names(self):
        """
        Define a generic template to template name list.
        """
        templates = super(ListView, self).get_template_names()
        templates.append("forms/list.html")
        return templates

    def get_create_url(self):
        create_url = getattr(self, 'create_url', None)
        if not create_url is False:
            try:
                create_url = UrlHelper.make_by_model(self.model, CREATE)
            except NoReverseMatch:
                return create_url
        return create_url

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['create_url'] = self.get_create_url()
        return context