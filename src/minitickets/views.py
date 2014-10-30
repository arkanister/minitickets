# coding: utf-8
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from django.views.generic.base import View as DjangoView, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from lib.utils.views.base import SmartView as View, TemplateSmartView as TemplateView
from lib.utils.views.detail import DetailView
from lib.utils.views.edit import CreateView, UpdateView, DeleteView, ProcessFormView
from lib.utils.views.tables import SingleTableView as ListView
from lib.utils.views.utils import JsonResponse
from src.minitickets.forms import FuncionarioCreateForm, FuncionarioUpdateForm, ProdutoForm, \
    ClienteUpdateForm, ClienteCreateForm, TicketCreateForm, TicketDetailForm, TicketEncerrarForm, TicketReleaseForm
from src.minitickets.models import Funcionario, Produto, Cliente, Ticket, HistoricoTicket, TempoTicket
from src.minitickets.tables import FuncionarioTable, ProdutoTable, ClienteTable


class HomeView(TemplateView):
    template_name = 'home.html'
    breadcrumbs = False
    title = 'Home Page!'


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
        context['desenvolvedores'] = Funcionario.objects.filter(cargo=2, situacao=1)
        tempo = TempoTicket.objects.filter(ticket=self.object, funcionario=self.request.user, data_termino__isnull=True)

        if tempo.exists():
            context['has_started'] = True

        # retorna as horas trabalhadas por cada analista e desenvolvedor
        analista_tempo = sum([t.as_hours() for t in self.object.tempoticket_set.filter(funcionario__cargo=1)])
        desenvolvedor_tempo = sum([t.as_hours() for t in self.object.tempoticket_set.filter(funcionario__cargo=2)])
        total_tempo = analista_tempo + desenvolvedor_tempo

        context['tempo'] = {
            "analista": {
                "percent": (analista_tempo * 100) / total_tempo if total_tempo > 0 else 0,
                "total": analista_tempo
            },
            "desenvolvedor": {
                "percent": (desenvolvedor_tempo * 100) / total_tempo if total_tempo > 0 else 0,
                "total": desenvolvedor_tempo
            },
            "total": total_tempo
        }

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
            if self.request.user.cargo == 1:
                de = self.request.GET.get('de')
                if de is not None:
                    queryset = queryset.filter(desenvolvedor=de).exclude(situacao=2)
                else:
                    queryset = queryset.filter(Q(situacao=1, desenvolvedor__isnull=True) | Q(situacao=3))
            elif self.request.user.cargo == 2:
                queryset = queryset.filter(situacao=1)
            elif self.request.user.cargo == 3:
                queryset = queryset.exclude(situacao=2)
        else:
            queryset = queryset.filter(situacao=2)

        a = self.request.GET.get('a')
        if a == 'i':
            queryset = queryset.filter(analista__isnull=True)
        elif a is not None:
            queryset = queryset.filter(analista=a)

        return queryset.order_by('-situacao', 'data_abertura')

    def get_context_data(self, **kwargs):
        context = super(TicketListView, self).get_context_data(**kwargs)
        context['t'] = self.request.GET.get('t')
        context['s'] = self.request.GET.get('s')
        context['se'] = self.request.GET.get('se')

        analista = self.request.GET.get('a')
        if analista == 'i':
            analista = "Indefinidos"
        elif analista is not None:
            analista = Funcionario.objects.filter(pk=analista)
            if analista.exists():
                analista = analista.get()
        context['a'] = analista

        desenvolvedor = self.request.GET.get('de')
        if desenvolvedor == 'i':
            desenvolvedor = "Indefinidos"
        elif desenvolvedor is not None:
            desenvolvedor = Funcionario.objects.filter(pk=desenvolvedor)
            if desenvolvedor.exists():
                desenvolvedor = desenvolvedor.get()
        context['de'] = desenvolvedor

        started_ticket = self.request.user.tempoticket_set.filter(data_termino__isnull=True)
        if started_ticket.exists():
            started_ticket = started_ticket.get()
            context['started_ticket'] = started_ticket.ticket

        context['analistas'] = Funcionario.objects.filter(cargo=1, situacao=1)
        context['desenvolvedores'] = Funcionario.objects.filter(
            cargo=2, situacao=1,
            desenvolvedor__analista__pk=self.request.user.pk
        ).distinct()
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
            'historico': history.render()
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
        form.fields['desenvolvedor'].queryset = Funcionario.objects.filter(cargo=2, situacao=1)
        return form

    def form_valid(self, form):
        self.object = form.save()
        history = HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo="%s repassou o ticket para %s." % (unicode(self.request.user), unicode(self.object.desenvolvedor))
        )
        return JsonResponse({'historico': history.render()})

    def form_invalid(self, form):
        error = form.errors['desenvolvedor'][0]
        return JsonResponse(error, status=400)


class TicketAnalistaUpdateView(UpdateView):
    breadcrumbs = False
    model = Ticket
    fields = ['analista']

    def get_form_kwargs(self):
        kwargs = super(TicketAnalistaUpdateView, self).get_form_kwargs()
        data = {'analista': self.request.POST.get('value')}
        kwargs['data'] = data
        return kwargs

    def get_form(self, form_class):
        form = super(TicketAnalistaUpdateView, self).get_form(form_class)
        form.fields['analista'].required = True
        form.fields['analista'].queryset = Funcionario.objects.filter(cargo=1, situacao=1)
        return form

    def form_valid(self, form):
        self.object = form.save()
        HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo="%s repassou o ticket para %s." % (unicode(self.request.user), unicode(self.object.analista))
        )
        return JsonResponse({})

    def form_invalid(self, form):
        error = form.errors['desenvolvedor'][0]
        return JsonResponse(error, status=400)


class TicketReOpenUpdateView(UpdateView):
    model = Ticket
    form_class = TicketReleaseForm
    template_name = "minitickets/ticket_release_form.html"
    title = u"[icon:reply] Reopen Ticket"

    success_message = u"[icon:check] Ticket <b>[titulo]</b> reaberto com sucesso!"

    def get_success_url(self):
        return reverse("minitickets:list-ticket")

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.situacao = 1
        self.object.save()

        HistoricoTicket.objects.create_historico(
            criado_por=self.request.user,
            ticket=self.object,
            conteudo=form.cleaned_data.get("historico"),
            tipo=2
        )

        HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo=u"Ticket reaberto pelo usuário %s." % unicode(self.request.user)
        )

        self.messages.success(self.get_message("success"))

        return JsonResponse({
            "redirect_to": self.get_success_url()
        })


class TicketReleaseUpdateView(UpdateView):
    model = Ticket
    form_class = TicketReleaseForm
    template_name = "minitickets/ticket_release_form.html"
    title = u"[icon:check] Release Ticket"

    success_message = u"[icon:check] Ticket <b>[titulo]</b> liberado com sucesso!"

    def get_success_url(self):
        return reverse("minitickets:list-ticket")

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.situacao = 3
        self.object.save()

        HistoricoTicket.objects.create_historico(
            criado_por=self.request.user,
            ticket=self.object,
            conteudo=form.cleaned_data.get("historico"),
            tipo=2
        )

        HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo=u"Ticket liberado pelo usuário %s." % unicode(self.request.user)
        )

        self.messages.success(self.get_message("success"))

        return JsonResponse({
            "redirect_to": self.get_success_url()
        })


class TicketEncerrarUpdateView(UpdateView):
    model = Ticket
    form_class = TicketEncerrarForm
    template_name = "minitickets/ticket_encerrar_form.html"
    title = u"[icon:times] Encerrar Ticket"

    def get_success_url(self):
        return reverse("minitickets:detail-ticket", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.data_fechamento = timezone.now()
        self.object.situacao = 2
        self.object.save()

        HistoricoTicket.objects.create_historico(
            ticket=self.object,
            conteudo=u"Ticket encerrado pelo usuário %s." % unicode(self.request.user)
        )

        return JsonResponse({
            "redirect_to": self.get_success_url()
        })
# </editor-fold>


# <editor-fold desc="HistoricoTicket">
class HistoricoTicketCreateView(CreateView):
    model = HistoricoTicket
    prefix = 'history'
    fields = ['conteudo']
    ajax_required = True

    def form_valid(self, form):
        ticket = Ticket.objects.get(pk=self.kwargs.get('ticket'))
        self.object = self.model.objects.create_historico(
            ticket=ticket,
            conteudo=form.cleaned_data.get('conteudo'),
            criado_por=self.request.user,
            tipo=2
        )
        return JsonResponse({'historico': self.object.render()})
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

        return JsonResponse({'historico': history.render()})


class TempoTicketPauseView(View):
    breadcrumbs = False
    model = TempoTicket

    def post(self, request, *args, **kwargs):
        user = request.user.pk

        self.object = self.model.objects.filter(funcionario=user, ticket=kwargs.get('ticket'), data_termino__isnull=True)[0]
        self.object, history = self.model.objects.pause(self.object)

        return JsonResponse({'historico': history.render()})
# </editor-fold>


