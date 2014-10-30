# coding: utf-8

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import ugettext as _
from lib.utils import forms as forms_utils
from django.db.models import Q
from lib.utils.forms.widgets import CheckboxSelectMultiple
from src.minitickets.models import Funcionario, Produto, Cliente, Ticket, TempoTicket


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
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")},
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    password1 = forms.CharField(label=_("Password"), max_length=128, widget=forms.PasswordInput())
    password2 = forms.CharField(label=_("Password confirmation"), max_length=128, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(FuncionarioCreateForm, self).__init__(*args, **kwargs)
        opts = getattr(self._meta.model, '_meta')
        self.fields['cargo'].choices = opts.get_field('cargo').choices

    class Meta:
        model = Funcionario
        widgets = {
            'nome': forms.TextInput(attrs={"size": 40}),
            'cargo': forms_utils.InlineRadioSelect,
            'cpf': forms.TextInput(attrs={"data-input-mask": 'cpf'}),
            'email': forms_utils.EmailIconInput(),
        }
        fields = ['nome', 'email', 'cpf', 'rg', 'cargo',
                  'username', 'password1', 'password2']

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            Funcionario.objects.get(nome_usuario=username)
        except Funcionario.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        data = self.cleaned_data
        del data['password2']

        instance = Funcionario.objects.create_user(
            nome_usuario=data.pop('username'),
            nome=data.pop('nome'),
            email=data.pop('email'),
            cargo=data.pop('cargo'),
            password=data.pop('password1'),
            **data
        )
        return instance


class FuncionarioUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FuncionarioUpdateForm, self).__init__(*args, **kwargs)
        opts = getattr(self._meta.model, '_meta')
        self.fields['cargo'].choices = opts.get_field('cargo').choices

    class Meta:
        model = Funcionario
        widgets = {
            'nome': forms.TextInput(attrs={"size": 40}),
            'cpf': forms.TextInput(attrs={"data-input-mask": 'cpf'}),
            'email': forms_utils.EmailIconInput(),
            'cargo': forms_utils.InlineRadioSelect
        }
        fields = ['nome', 'email', 'cpf', 'rg', 'cargo', 'situacao']
# </editor-fold>


# <editor-fold desc="Produto">
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        widgets = {'descricao': forms.Textarea(attrs={"rows": 5})}
        exclude = ['situacao']
# </editor-fold>


# <editor-fold desc="Cliente">
class ClienteCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClienteCreateForm, self).__init__(*args, **kwargs)
        self.fields['produtos'].help_text = None
        queryset = self.fields['produtos'].queryset
        self.fields['produtos'].queryset = queryset.filter(situacao=1)

    class Meta:
        model = Cliente
        widgets = {
            'cnpj': forms.TextInput(attrs={"data-input-mask": 'cnpj'}),
            'nome_fantasia': forms.TextInput(attrs={"size": '60'}),
            'razao_social': forms.TextInput(attrs={"size": '60'}),
            'nome_diretor': forms.TextInput(attrs={"size": '40'}),
            'email': forms_utils.EmailIconInput(),
            'telefone': forms.TextInput(attrs={"data-input-mask": 'telefone'}),
            'produtos': CheckboxSelectMultiple()
        }
        fields = ['nome_fantasia', 'razao_social', 'cnpj', 'inscricao_estadual', 'inscricao_municipal', 'nome_diretor', 'telefone', 'email',  'produtos']


class ClienteUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClienteUpdateForm, self).__init__(*args, **kwargs)
        self.fields['produtos'].help_text = None
        queryset = self.fields['produtos'].queryset
        self.fields['produtos'].queryset = queryset.filter(Q(situacao=1) | Q(cliente__pk=self.instance.pk)).distinct()

    class Meta:
        model = Cliente
        widgets = {
            'cnpj': forms.TextInput(attrs={"data-input-mask": 'cnpj'}),
            'nome_fantasia': forms.TextInput(attrs={"size": '60'}),
            'razao_social': forms.TextInput(attrs={"size": '60'}),
            'nome_diretor': forms.TextInput(attrs={"size": '40'}),
            'email': forms_utils.EmailIconInput(),
            'telefone': forms.TextInput(attrs={"data-input-mask": 'telefone'}),
            'produtos': CheckboxSelectMultiple()
        }
        fields = ['nome_fantasia', 'razao_social', 'cnpj', 'inscricao_estadual', 'inscricao_municipal', 'nome_diretor', 'telefone', 'email',  'produtos', 'situacao']

# </editor-fold>


# <editor-fold desc="Ticket">
class TicketCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        widgets = {
            'cliente': forms.HiddenInput(),
            'produto': forms.Select(attrs={"class": "form-control"}),
            'titulo': forms.TextInput(attrs={"class": "form-control", "placeholder": u"Título do Ticket"}),
            'descricao': forms.Textarea(attrs={"class": "custom-scroll md-input", "class": "mymarkdown", "rows": 4, "placeholder": "Descreva aqui o ticket."}),
            'tipo': forms.Select(attrs={"class": "form-control"})
        }
        forms.CheckboxSelectMultiple
        fields = ['cliente', 'produto', 'tipo', 'titulo', 'descricao']


class TicketDetailForm(forms.ModelForm):
    model = Ticket
    widgets = {
        'desenvolvedor': forms.Select(attrs={"class": "form-control"})

    }


class TicketUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        widgets = {
            'cliente': forms.HiddenInput(),
            'produto': forms.Select(),
            'analista': forms.Select(),
            'titulo': forms.TextInput(),
            'descricao': forms.Textarea(attrs={"class": "custom-scroll md-input", "id": "mymarkdown", "rows": 5}),
            'tipo': forms_utils.InlineRadioSelect
        }
        fields = ['cliente', 'produto', 'titulo', 'descricao', 'tipo']


class TicketReleaseForm(forms.Form):

    def __init__(self, instance=None, *args, **kwargs):
        super(TicketReleaseForm, self).__init__(*args, **kwargs)
        self.instance = instance

    historico = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-scroll md-input", "class": "mymarkdown", "rows": 4, "placeholder": "Digite a solução do ticket."}))


class TicketEncerrarForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketEncerrarForm, self).__init__(*args, **kwargs)
        self.fields['solucao'].required = True

    class Meta:
        model = Ticket
        widgets = {
            'solucao': forms.Textarea(attrs={"class": "custom-scroll md-input", "class": "mymarkdown", "rows": 4, "placeholder": "Digite a solução do ticket."}),
        }
        fields = ['solucao']
# </editor-fold>
