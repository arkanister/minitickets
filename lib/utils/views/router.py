# -*- coding: utf-8 -*-

from django.db import models
from django.conf.urls import url
from django.utils.importlib import import_module

from .edit import CreateView, UpdateView, DeleteView
from .detail import DetailView
from .list import ListView

from .types import CREATE, UPDATE, DELETE, DETAIL, LIST

NAMES = ("add", "change", "delete", "detail", "list")
VIEWS = ((CREATE, CreateView), (UPDATE, UpdateView), (DELETE, DeleteView),
         (DETAIL, DetailView), (LIST, ListView))


class Router(object):
    def __init__(self, *args):
        self.models = []
        for app in args:
            self.register(app)

    def register(self, app):
        module = import_module(".models", app)
        for model in models.get_models(module):
            self.models.append(model)

    @staticmethod
    def import_module(name):
        try:
            return import_module(name)
        except ImportError:
            # name import does not exists
            return None

    @staticmethod
    def get_name(object_name, _type, suffix):
        names = ["Create", "Update", "Delete", "Detail", "List"]
        return object_name + names[_type - 1] + suffix

    @staticmethod
    def get_view(model, default_class, _type=None, view_name_suffix="View",
                 form_name_suffix="Form"):
        _module = model.__module__.split(".")[:-1]
        _type = _type or getattr(default_class, "_TYPE")
        _opts = getattr(model, '_meta')

        views = Router.import_module(".".join(_module + ["views"]))
        forms = Router.import_module(".".join(_module + ["forms"]))

        object_name = _opts.object_name

        view_names = Router.get_name(object_name, _type, view_name_suffix)
        form_names = [Router.get_name(object_name, _type, form_name_suffix),
                      object_name + form_name_suffix]

        if not hasattr(views, view_names):
            # create a generic view
            kwargs = {"model": model}
            if _type in (CREATE, UPDATE):
                # find a form to view
                for form in form_names:
                    if hasattr(forms, form):
                        kwargs.update({"form_class": getattr(forms, form)})
                        break
            return default_class.as_view(**kwargs)
        return getattr(views, view_names).as_view()

    @staticmethod
    def get_regex(_type):
        regex, regex_suffix = r"^%s/%s/", r"$"
        if _type in (UPDATE, DELETE, DETAIL):
            regex += r"(?P<pk>\d+)/"
        elif _type == LIST:
            regex = r'^%s/'
        return regex + regex_suffix

    @staticmethod
    def get_url_name(_type, url_separator="-"):
        return NAMES[_type - 1] + url_separator + "%s"

    @staticmethod
    def make_view(model):
        urls = []
        opts = getattr(model, '_meta')

        for _type, View in VIEWS:
            regex = Router.get_regex(_type)
            object_name = opts.object_name.lower()
            url_name = Router.get_url_name(_type) % object_name
            view = Router.get_view(model, default_class=View, _type=_type)
            if _type == LIST:
                object_name += 's'
                regex = regex % object_name
            else:
                regex = regex % (NAMES[_type - 1], object_name)
            urls.append(url(regex, view, name=url_name))
        return urls

    def get_urls(self):
        urls = []
        for model in self.models:
            urls += Router.make_view(model)
        return urls