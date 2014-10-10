# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponseRedirect
from django.template import loader
from django.utils.translation import ugettext as _
from .utils import HtmlEmailSender
from ..base import SmartView as View


class EmailTemplateRenderMixin(object):
    email_template_name = None

    def get_email_template_names(self):
        if self.email_template_name is None:
            raise ImproperlyConfigured(
                _("EmailTemplateRenderMixin requires either a definition of "
                  "'template_name' or an implementation of 'get_email_template_names()'"))
        return self.email_template_name

    def get_email_context_data(self, **kwargs):
        return kwargs

    def render_email(self, **kwargs):
        template = loader.get_template(self.get_email_template_names())
        context = loader.Context(self.get_email_context_data(**kwargs))
        return template.render(context)


class EmailMixin(EmailTemplateRenderMixin):
    email_sender = HtmlEmailSender
    email_subject = None
    email_to = None

    def get_email_subject(self):
        return getattr(self, 'email_subject', None)

    def get_email_to_list(self):
        user_email = getattr(self.request.user, 'email', None)
        email_to = getattr(self, 'email_to', None)
        if email_to is not None and isinstance(email_to, basestring):
            return [email_to]
        elif email_to is not None and isinstance(email_to, (list, tuple)):
            return email_to
        elif email_to is None and user_email is not None:
            return [user_email]
        else:
            raise ImproperlyConfigured(
                _("EmailTemplateRenderMixin requires either a definition of "
                  "'email_to' or an implementation of 'get_email_to_list()'."))

    def send_email(self, **kwargs):
        """ Send email. """
        self.email_sender(
            subject=self.get_email_subject(),
            to_email=self.get_email_to_list(),
            content=self.render_email(**kwargs)
        ).send()


class EmailView(EmailMixin, View):
    _default_template_messages = {
        'success': _('Email sent succesfully!'),
        'error': _('Failed to send mail!')
    }

    def get_success_url(self):
        success_url = getattr(self, 'success_url', None)
        if not success_url:
            raise ImproperlyConfigured(
                _("EmailView requires either a definition of "
                  "'success_url' or an implementation of 'get_success_url()'."))
        return success_url

    def get(self, request, *args, **kwargs):
        try:
            self.send_email()
            self.messages.success(self.get_message('success'))
        except Exception, e:
            self.messages.error(self.get_message('error'))
            if hasattr(self, 'send_email_error'):
                return self.send_email_error(e.message)
        return HttpResponseRedirect(self.get_success_url())
