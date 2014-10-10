# coding: utf-8
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import View as DjangoView

from lib.utils.views.base import SmartView as View, TemplateSmartView as TemplateView
from lib.utils.views.detail import DetailView
from lib.utils.views.edit import CreateView, UpdateView, DeleteView
from lib.utils.views.tables import SingleTableView as ListView
from lib.utils.views.utils import JsonResponse
from src.minitickets.forms import FuncionarioCreateForm, FuncionarioUpdateForm, ProdutoForm, \
    ClienteUpdateForm, ClienteCreateForm, TicketCreateForm, TicketDetailForm
from src.minitickets.models import Funcionario, Produto, Cliente, Ticket, HistoricoTicket, TempoTicket
from src.minitickets.tables import FuncionarioTable, ProdutoTable, ClienteTable


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'


def teste(request):
    return render(request, template_name='teste-modal.html')


# <editor-fold desc="Funcionario">
class FuncionarioCreateView(CreateView):
    model = Funcionario
    form_class = FuncionarioCreateForm


class FuncionarioUpdateView(UpdateView):
    model = Funcionario
    form_class = FuncionarioUpdateForm


class FuncionarioListView(ListView):
    model = Funcionario
    table_class = FuncionarioTable


class FuncionarioDeleteView(DeleteView):
    model = Funcionario
# </editor-fold>


# <editor-fold desc="Cliente">
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteCreateForm


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteUpdateForm


class ClienteListView(ListView):
    model = Cliente
    table_class = ClienteTable


class ClienteDeleteView(DeleteView):
    model = Cliente


class ClienteAutoCompleteView(DjangoView):
    model = Cliente

    def get_queryset(self):
        '''
        Metodo para buscar os cliente no banco atraves do termo = term
        :return: QueryDict
        '''
        queryset = self.model.objects.filter(
            nome_fantasia__istartswith=self.request.POST.get("term"),
            situacao=1, produtos__pk__isnull=False).distinct()
        return queryset

    def post(self, request, *args, **kwargs):
        '''
        Metodo que retorna uma lista de clientes
        :param request:
        :param args:
        :param kwargs:
        :return: JsonResponse
        '''
        queryset = self.get_queryset()
        return JsonResponse([{
            "label": cliente.nome_fantasia,
            "value": cliente.nome_fantasia,
            "id": cliente.id,
            "products": [{"id": produto.id, "label": unicode(produto)} for produto in cliente.produtos.all()]
        } for cliente in queryset])
# </editor-fold>


# <editor-fold desc="Produto">
class ProdutoCreateView(CreateView):
    model = Produto
    fields = ['nome', 'descricao']
    form_class = ProdutoForm


class ProdutoUpdateView(UpdateView):
    model = Produto


class ProdutoListView(ListView):
    model = Produto
    table_class = ProdutoTable


class ProdutoDeleteView(DeleteView):
    model = Produto
# </editor-fold>


# <editor-fold desc="Ticket">
class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketCreateForm

    def form_valid(self, form):
        if self.request.user.cargo == 1:
            form.instance.analista = self.request.user

        self.object = form.save()
        self.messages.success(self.get_message('success'))
        return JsonResponse({'redirect_to': self.get_success_url()})


class TicketDetailView(DetailView):
    model = Ticket
    form_class = TicketDetailForm

    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        context['desenvolvedores'] = Funcionario.objects.filter(cargo=1, situacao=1)  # TODO: cargo=2
        tempo = TempoTicket.objects.filter(ticket=self.object, funcionario=self.request.user, data_termino__isnull=True)
        if tempo.exists():
            context['has_started'] = True
        return context


class TicketListView(ListView):
    model = Ticket
    actions = False

    def get_queryset(self):
        queryset = super(TicketListView, self).get_queryset()

        funcionario = self.request.user

        if funcionario.cargo == 1:
            queryset = queryset.filter(analista=funcionario.pk)
        elif funcionario.cargo == 2:
            queryset = queryset.filter(desenvolvedor=funcionario.pk)
        elif funcionario.cargo == 3:
            # Se for gerente apenas apresenta todos os tickets
            pass

        se = self.request.GET.get('se')
        if se is not None:
            queryset = queryset.filter(Q(titulo__icontains=se) | Q(descricao__icontains=se))

        t = self.request.GET.get('t')
        if t is not None:
            queryset = queryset.filter(tipo=t)

        s = self.request.GET.get('s')
        if s is None or s == 'open':
            queryset = queryset.filter(situacao=1)
        else:
            queryset = queryset.filter(situacao=2)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TicketListView, self).get_context_data(**kwargs)
        context['t'] = self.request.GET.get('t')
        context['s'] = self.request.GET.get('s')
        context['se'] = self.request.GET.get('se')

        started_ticket = self.request.user.tempoticket_set.filter(data_termino__isnull=True)
        if started_ticket.exists():
            started_ticket = started_ticket.get()
            context['started_ticket'] = started_ticket.ticket

        return context


class TicketTipoUpdateView(UpdateView):
    breadcrumbs = False
    model = Ticket
    fields = ['tipo']

    def get_form_kwargs(self):
        kwargs = super(TicketTipoUpdateView, self).get_form_kwargs()
        data = {'tipo': self.request.POST.get('value')}
        kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        history = HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo="%s alterou o tipo do ticket para %s." % (unicode(self.request.user), self.object.get_tipo_display())
        )
        return JsonResponse({
            'tipo': self.object.tipo,
            'tipo_display': self.object.get_tipo_display(),
            'conteudo': history.conteudo,
            'data_cadastro': history.data_cadastro.strftime('%Y-%m-%d %H:%M')
        })


class TicketDesenvolvedorUpdateView(UpdateView):
    breadcrumbs = False
    model = Ticket
    fields = ['desenvolvedor']

    def get_form_kwargs(self):
        kwargs = super(TicketDesenvolvedorUpdateView, self).get_form_kwargs()
        data = {'desenvolvedor': self.request.POST.get('value')}
        kwargs['data'] = data
        return kwargs

    def get_form(self, form_class):
        form = super(TicketDesenvolvedorUpdateView, self).get_form(form_class)
        form.fields['desenvolvedor'].required = True
        form.fields['desenvolvedor'].queryset = Funcionario.objects.filter(cargo=1, situacao=1)  # TODO: cargo=2
        return form

    def form_valid(self, form):
        self.object = form.save()
        history = HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo="%s repassou o ticket para %s." % (unicode(self.request.user), unicode(self.object.desenvolvedor))
        )
        return JsonResponse({
            'conteudo': history.conteudo,
            'data_cadastro': history.data_cadastro.strftime('%Y-%m-%d %H:%M')
        })

    def form_invalid(self, form):
        error = form.errors['desenvolvedor'][0]
        return JsonResponse(error, status=400)
# </editor-fold>


# <editor-fold desc="HistoricoTicket">
class HistoricoTicketCreateView(CreateView):
    model = HistoricoTicket
    prefix = 'history'
    fields = ['conteudo']
    ajax_required = True

    def form_valid(self, form):
        ticket = Ticket.objects.get(pk=self.kwargs.get('ticket'))
        self.object = self.model.objects.create_historico(ticket, form.cleaned_data.get('conteudo'), self.request.user)
        return JsonResponse({
            'criado_por': unicode(self.object.criado_por),
            'conteudo': self.object.conteudo,
            'data_cadastro': self.object.data_cadastro.strftime('%Y-%m-%d %H:%M')
        })
# </editor-fold>


# <editor-fold desc="TempoTicket">
class TempoTicketCreateView(View):
    breadcrumbs = False
    model = TempoTicket

    def post(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(pk=kwargs.get('ticket'))
        user = request.user

        if ticket.tempoticket_set.filter(funcionario=user.pk, data_termino__isnull=True).exists():
            raise PermissionDenied()

        user_tempo_ticket = user.tempoticket_set.filter(data_termino__isnull=True)
        if user_tempo_ticket.exists():
            user_tempo_ticket = user_tempo_ticket.get()
            TempoTicket.objects.pause(user_tempo_ticket)

        self.object, history = self.model.objects.start(ticket, user)

        return JsonResponse({
            'conteudo': history.conteudo,
            'data_cadastro': history.data_cadastro.strftime('%Y-%m-%d %H:%M')
        })


class TempoTicketPauseView(View):
    breadcrumbs = False
    model = TempoTicket

    def post(self, request, *args, **kwargs):
        user = request.user.pk

        self.object = self.model.objects.filter(funcionario=user, ticket=kwargs.get('ticket'), data_termino__isnull=True)[0]
        self.object, history = self.model.objects.pause(self.object)

        return JsonResponse({
            'conteudo': history.conteudo,
            'data_cadastro': history.data_cadastro.strftime('%Y-%m-%d %H:%M')
        })
# </editor-fold>
