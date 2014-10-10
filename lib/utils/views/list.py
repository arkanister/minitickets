# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
from django.template import loader

from django.views.generic.list import MultipleObjectMixin,\
    MultipleObjectTemplateResponseMixin
from django.http.response import Http404, HttpResponse
from django.utils.translation import ugettext as _
from .base import SmartView as View, DjangoView, ContextMixin
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


class GetModelOptionsView(ContextMixin, DjangoView):
    model = None
    object_list = None

    def get_queryset(self, **kwargs):
        if self.model is None:
            raise ImproperlyConfigured("please set a model to view.")
        if not kwargs:
            return self.model.objects.all()
        else:
            return self.model.objects.filter(**kwargs).distinct()

    def get_queryset_kwargs(self, **kwargs):
        names = self.request.GET.getlist("f[name]", [])
        values = self.request.GET.getlist("f[value]", [])
        kwargs.update(
            dict([(name, value) for name, value in zip(names, values)])
        )
        return kwargs

    def get_template(self):
        if hasattr(self, "template_name"):
            return loader.get_template(self.get_template_name())
        return loader.get_template_from_string(
            u"{% for option in object_list %}" + \
            u'<option value="{{ option.pk }}">{{ option }}</option>' + \
            u"{% endfor %}"
        )

    def get(self, request, *args, **kwargs):
        self.object_list = ['----------'] + list(self.get_queryset(**self.get_queryset_kwargs()))
        template = self.get_template()
        context = loader.Context(self.get_context_data(object_list=self.object_list))
        return HttpResponse(template.render(context))