# -*- coding: utf-8 -*-

from django.core.mail import EmailMessage
from django.utils.encoding import force_unicode
from django.core.mail.message import EmailMultiAlternatives
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string


class EmailSender(object):
    sender = EmailMessage

    def __init__(self, subject, to_email, content):
        self.subject = subject
        self.content = content
        self.to_email = isinstance(to_email, (list, tuple)) and to_email or [to_email]

    def send(self):
        self.sender(subject=self.subject, message=self.content, recipient_list=self.to_email).send()


class HtmlEmailSender(EmailSender):
    sender = EmailMultiAlternatives

    def send(self):
        email = EmailMultiAlternatives(self.subject, striptags(self.content), to=self.to_email)
        email.attach_alternative(self.content, "text/html")
        email.send()