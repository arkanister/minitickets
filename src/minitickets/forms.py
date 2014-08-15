# coding: utf-8

from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from lib.utils.forms.widgets import InputIconWidget


class AuthenticationForm(BaseAuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = InputIconWidget('user',
            render_type=InputIconWidget.INPUT_ICON,
            attrs={'placeholder': u'Usuário'})

        self.fields['password'].widget = InputIconWidget('lock',
            render_type=InputIconWidget.INPUT_ICON,
            attrs={'placeholder': 'Senha'},
            input_type="password")