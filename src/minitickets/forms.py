# coding: utf-8

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from lib.utils import forms as forms_utils
from src.minitickets.models import Funcionario


class AuthenticationForm(BaseAuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms_utils.TextIconInput('user',
            format=forms_utils.TextIconInput.FORMAT_ICON,
            attrs={'placeholder': u'Usuário'}
        )

        self.fields['password'].widget = forms_utils.PasswordIconInput('lock',
            format=forms_utils.PasswordIconInput.FORMAT_ICON,
            attrs={'placeholder': 'Senha'}
        )


# <editor-fold desc="Funcionário">
class FuncionarioCreateForm(forms.ModelForm):

    password1 = forms.CharField(max_length=128, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=128, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(FuncionarioCreateForm, self).__init__(*args, **kwargs)
        opts = getattr(self._meta.model, '_meta')
        self.fields['cargo'].choices = opts.get_field('cargo').choices

    class Meta:
        model = Funcionario
        widgets = {
            'nome': forms.TextInput(attrs={"size": 40}),
            'cargo': forms_utils.InlineRadioSelect,
            'cpf': forms.TextInput(attrs={'data-mask': 'cpf'}),
            'email': forms_utils.EmailIconInput
        }
        fields = ['nome', 'email', 'cpf', 'rg', 'cargo', 'nome_usuario', 'password1', 'password2']
# </editor-fold>