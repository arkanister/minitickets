# -*- coding: utf-8 -*-
from django.conf import settings

from django.db import models
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.utils.translation import ugettext as _
from django.views.generic.edit import ModelFormMixin as DjangoModelFormMixin
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponseRedirect

from .base import SmartView as View
from .types import CREATE, UPDATE, DELETE, LIST
from .utils import UrlHelper
from .detail import BaseDetailView


class LogMixin(object):

    """
    Um mixin para criar automaticamente o
    log após salvar o objeto.

    Para não criar o log use na view:
    action_flag = False
    """
    log_class = getattr(settings, "LOG_USER_MODEL", None)

    def get_log_class(self):
        if isinstance(self.log_class, basestring):
            try:
                self.log_class = models.get_model(*self.log_class.split('.'))
            except ImportError:
                raise ImproperlyConfigured("Define the log class")
        if self.log_class is False:
            return None
        return self.log_class

    def get_action_flag(self):
        action_flag = getattr(self, "action_flag", None)

        # if action_flag is False does nothing
        if action_flag is not False and action_flag is None:
            action_flag = getattr(self, '_TYPE', None)
        return action_flag

    def create_log(self):
        action_flag = self.get_action_flag()

        # if action_flag is False does nothing
        if action_flag is not False:
            log = self.get_log_class()
            if not log is None:
                log.objects.log_action(self.request.user, self.object, action_flag)

    def form_valid(self, form):
        response = super(LogMixin, self).form_valid(form)
        self.create_log()
        return response


class ModelFormMixin(LogMixin, DjangoModelFormMixin):
    next_field_name = 'next'

    def get_url_args(self, view_type, *args):
        """ a helper to get url args """
        return args

    def get_url_kwargs(self, view_type, **kwargs):
        """ a helper to get url kwargs """
        return kwargs

    def get_url_redirect(self, view_type, *args, **kwargs):
        """
        Return a redirect url.
        """
        args = self.get_url_args(view_type, *args)
        kwargs = self.get_url_kwargs(view_type, **kwargs)
        return UrlHelper.make_by_model(self.model, view_type, args=args, kwargs=kwargs)

    def get_success_url(self):
        """
        Returns a success redirect.
        """
        next_url = self.request.POST.get(self.next_field_name, None) or \
                   self.request.GET.get(self.next_field_name, None)

        if next_url is not None:
            return next_url

        if "_addanother" in self.request.POST:
            return self.get_url_redirect(CREATE)

        if "_continue" in self.request.POST:
            return self.get_url_redirect(UPDATE, pk=self.object.pk)

        if not self.success_url:
            return self.get_url_redirect(LIST)

        return super(ModelFormMixin, self).get_success_url()

    def form_valid(self, form):
        response = super(ModelFormMixin, self).form_valid(form)
        if form.changed_data:
            self.messages.success(self.get_message('success'))
        return response

    def form_invalid(self, form):
        response = super(ModelFormMixin, self).form_invalid(form)
        self.messages.error(self.get_message('error'))
        return response

    def get_breadcrumbs(self):
        breadcrumbs = super(ModelFormMixin, self).get_breadcrumbs()
        if breadcrumbs is not None:
            opts = getattr(self.model, '_meta')
            breadcrumbs.add(opts.verbose_name_plural.title(), url=self.get_url_redirect(LIST), index=1)
            return breadcrumbs
        return None


class ProcessFormView(View):
    """
    A mixin that renders a form on GET and processes it on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseCreateView(ModelFormMixin, ProcessFormView):
    """
    Base view for creating an new object instance.

    Using this base class requires subclassing to provide a response mixin.
    """

    _TYPE = CREATE

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).post(request, *args, **kwargs)


class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    """
    View for creating a new object instance,
    with a response rendered by template.
    """
    template_name_suffix = '_form'
    _default_template_messages = {
        "success": _("[verbose_name] '[unicode]' created!"),
        "error": _("Failed to create [verbose_name]!")
    }

    def get_title(self):
        title = super(CreateView, self).get_title()
        if not getattr(self, 'title', None):
            title = _("Create %s") % title
        return title

    def get_template_names(self):
        """
        Define a generic template to template name list.
        """
        templates = super(CreateView, self).get_template_names()
        opts = getattr(self.model, '_meta')
        templates.append("%s/%s_%s_form.html" % (opts.app_label.lower(), opts.object_name.lower(), 'create'))
        templates.append("forms/%s_form.html" % 'create')
        templates.append("forms/form.html")
        return templates


class BaseUpdateView(ModelFormMixin, ProcessFormView):
    """
    Base view for updating an existing object.

    Using this base class requires subclassing to provide a response mixin.
    """

    _TYPE = UPDATE

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView):
    """
    View for updating an object,
    with a response rendered by template.
    """
    template_name_suffix = '_form'
    _default_template_messages = {
        "success": _("[verbose_name] '[unicode]' successfully modified!"),
        "error": _("Failed to modify [verbose_name]!")
    }

    def get_title(self):
        title = super(UpdateView, self).get_title()
        if not getattr(self, 'title', None):
            title = _("Update %s") % title
        return title

    def get_template_names(self):
        """
        Define a generic template to template name list.
        """
        templates = super(UpdateView, self).get_template_names()
        opts = getattr(self.model, '_meta')
        templates.append("%s/%s_%s_form.html" % (opts.app_label.lower(), opts.object_name.lower(), 'update'))
        templates.append("forms/%s_form.html" % 'update')
        templates.append("forms/form.html")
        return templates


class DeletionMixin(LogMixin):
    """
    A mixin providing the ability to delete objects
    """
    success_url = None
    next_field_name = 'next'

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        self.create_log()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    # Add support for browsers which only accept GET and POST for now.
    def post(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get_url_args(self, view_type, *args):
        """ a helper to get url args """
        return args

    def get_url_kwargs(self, view_type, **kwargs):
        """ a helper to get url kwargs """
        return kwargs

    def get_url_redirect(self, view_type, *args, **kwargs):
        """
        Return a redirect url.
        """
        try:
            return UrlHelper.make_by_model(self.model, view_type,
                                           *self.get_url_args(view_type, *args),
                                           **self.get_url_kwargs(view_type, **kwargs))
        except Exception:
            message = _("Please check url to %s args.")
            raise Exception(message % view_type)

    def get_success_url(self):
        next_url = self.request.POST.get(self.next_field_name, None) or \
                   self.request.GET.get(self.next_field_name, None)

        if next_url is not None:
            return next_url

        if self.success_url is None:
            try:
                return self.get_url_redirect(LIST)
            except:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url.")
        return self.success_url


class BaseDeleteView(DeletionMixin, BaseDetailView):
    """
    Base view for deleting an object.

    Using this base class requires subclassing to provide a response mixin.
    """

    _TYPE = DELETE


class DeleteView(SingleObjectTemplateResponseMixin, BaseDeleteView):
    """
    View for deleting an object retrieved with `self.get_object()`,
    with a response rendered by template.
    """
    template_name_suffix = '_confirm_delete'
    _default_template_messages = {
        "success": _("[verbose_name] '[unicode]' successfully deleted!"),
        "error": _("Failed to delete [verbose_name] '[unicode]'!")
    }

    def get_template_names(self):
        """
        Define a generic template to template name list.
        """
        templates = super(DeleteView, self).get_template_names()
        templates.append("forms/confirm_delete.html")
        return templates

    def get_title(self):
        title = super(DeleteView, self).get_title()
        if not getattr(self, 'title', None):
            title = _("Delete %s") % title
        return title

    def get_breadcrumbs(self):
        breadcrumbs = super(DeleteView, self).get_breadcrumbs()
        opts = getattr(self.model, '_meta')
        breadcrumbs.add(opts.verbose_name_plural, url=self.get_url_redirect(LIST), index=0)
        return breadcrumbs

    def delete(self, request, *args, **kwargs):
        response = super(DeleteView, self).delete(request, *args, **kwargs)
        opts = getattr(self.model, '_meta')
        self.messages.success(self.get_message('success'))
        return response