# coding: utf-8

import os
import json

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import loader
from django.utils import timezone
from lib.utils.models.validators import CpfValidator
from src.minitickets.managers import FuncionarioManager

PERMISSIONS = json.loads(open(
    os.path.join(
        settings.BASE_DIR, 'permissions.json')
).read())


class Pessoa(models.Model):
    email = models.EmailField(unique=True)
    situacao = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Ativo'),
            (2, 'Inativo')
        ),
        default=1
    )

    class Meta:
        abstract = True


class PessoaFisica(Pessoa):
    nome = models.CharField(max_length=80)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, validators=[CpfValidator()])
    rg = models.CharField(max_length=15, unique=True, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.cpf = self.cpf if not self.cpf == '' else None
        self.rg = self.rg if not self.rg == '' else None
        return super(PessoaFisica, self).save(*args, **kwargs)


class Funcionario(AbstractBaseUser, PessoaFisica):
    cargo = models.PositiveSmallIntegerField(
        choices=(
            (1, u'Analista'),
            (2, u'Desenvolvedor'),
            (3, u'Gerente')
        )
    )

    nome_usuario = models.CharField(max_length=50, unique=True)
    senha = models.CharField(max_length=128, help_text='Digite sua senha neste campo.')

    USERNAME_FIELD = 'nome_usuario'
    REQUIRED_FIELDS = ['nome', 'email', 'cargo']

    objects = FuncionarioManager()

    class Meta:
        verbose_name = u'Funcionário'

    def _is_active(self):
        return self.situacao == 1

    def _set_is_active(self, value):
        self.situacao = 1 if value else 2

    is_active = property(_is_active, _set_is_active)

    def _get_password(self):
        return self.senha

    def _set_password(self, value):
        self.senha = value

    password = property(_get_password, _set_password)

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split(' ')[0]

    def has_perm(self, perm, obj=None):
        user_permissions = PERMISSIONS[str(self.cargo)]
        return perm in user_permissions

    def has_perms(self, perms, obj=None):
        return all(self.has_perm(perm) for perm in perms)

    def __unicode__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField('Descrição', null=True, blank=True)
    situacao = models.PositiveIntegerField(
        choices=(
            (1, u'Ativo'),
            (2, u'Inativo')
        ),
        default = 1
    )

    def __unicode__(self):
        return self.nome


# <editor-fold desc="Cliente">
class Cliente(models.Model):
    nome_fantasia = models.CharField(max_length=80, blank=True, null=True)
    razao_social = models.CharField(max_length=80, unique=True)
    cnpj = models.CharField(max_length=18, unique=True)
    inscricao_estadual = models.CharField(max_length=20, unique=True, blank=True, null=True)
    inscricao_municipal = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nome_diretor = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=15, blank=True, null=True)
    produtos = models.ManyToManyField('Produto', blank=True, null=True)
    situacao = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Ativo'),
            (2, 'Inativo')
        ),
        default=1
    )

    def __unicode__(self):
        return self.razao_social

# </editor-fold>


# <editor-fold desc="Ticket">
class Ticket(models.Model):
    cliente = models.ForeignKey('Cliente')
    produto = models.ForeignKey('Produto')
    analista = models.ForeignKey('Funcionario', null=True, blank=True, related_name='analista')
    desenvolvedor = models.ForeignKey('Funcionario', null=True, blank=True, related_name='desenvolvedor')
    titulo = models.CharField(max_length=50)
    descricao = models.TextField()
    solucao = models.TextField(u'Solução', null=True, blank=True)
    tipo = models.PositiveSmallIntegerField(
        choices=(
            (1, u'Dúvida'),
            (2, u'Erro'),
            (3, u'Sugestão')
        ), default=1
    )
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    situacao = models.PositiveIntegerField(
        choices=(
            (1, 'Aberto'),
            (2, 'Fechado'),
            (3, 'Liberado')
        ), default=1
    )
# </editor-fold>


# <editor-fold desc="HistoricoTicket">
class HistoricoTicketManager(models.Manager):
    def create_historico(self, ticket, conteudo, criado_por=None, tipo=1):
        kwargs = {'ticket': ticket, 'conteudo': conteudo, "tipo": tipo}

        if criado_por is not None:
            kwargs['criado_por'] = criado_por

        instance = self.model(**kwargs)
        instance.save()

        return instance


class HistoricoTicket(models.Model):
    data_cadastro = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey('Funcionario', null=True, blank=True)
    ticket = models.ForeignKey('Ticket')
    conteudo = models.TextField()
    tipo = models.IntegerField(choices=(
        (1, u"Padrão"),
        (2, u"Comentário"),
        (3, u"Iniciar/Pausar")
    ))

    objects = HistoricoTicketManager()

    class Meta:
        ordering = ['-data_cadastro']

    def _get_icon_name(self):
        return 'warning' if self.tipo == 1 else ('comment' if self.tipo == 2 else 'clock-o')
    icon_name = property(_get_icon_name)

    def get_template(self):
        if self.tipo == 2:
            return (
                '{% load markdown_deux_tags %}{% load humanize %}{% load icon from icons %}'
                '<tr><td width="50%">{% icon icon_name "class"="text-muted bigger-120 no-padding" %}'
                '<strong> {{ criado_por }} </strong></td><td class="align-right">'
                '<em><time datetime="{{ data_cadastro|date:"Y-m-d H:i" }}">'
                '{% icon "clock-o" %} {{ data_cadastro|naturaltime }}</time></em>'
                '</td></tr><tr><td colspan="2">{{ conteudo|markdown }}</td></tr>'
            )
        else:
            return (
                '{% load markdown_deux_tags %}{% load humanize %}{% load icon from icons %}'
                '<tr><td width="50%">{% icon icon_name "class"="text-muted no-padding bigger-120" %}'
                ' {{ conteudo }}</td><td class="align-right">'
                '<em><time datetime="{{ data_cadastro|date:"Y-m-d H:i" }}">'
                '{% icon "clock-o" %} {{ data_cadastro|naturaltime }}</time></em>'
                '</td></tr><tr><td colspan="2"></td></tr>'
            )

    def render(self):
        context = loader.Context({
            'data_cadastro': self.data_cadastro,
            'conteudo': self.conteudo,
            'criado_por': self.criado_por,
            'icon_name': self.icon_name,
        })

        template = loader.get_template_from_string(self.get_template())
        return template.render(context)
# </editor-fold>


# <editor-fold desc="TempoTicket">
class TempoTicketManager(models.Manager):
    def start(self, ticket, funcionario):
        tempo_ticket = self.model(funcionario=funcionario, ticket=ticket)
        tempo_ticket.save()

        history = HistoricoTicket.objects.create_historico(
            ticket=ticket,
            conteudo="%s iniciou o ticket." % (unicode(funcionario)),
            tipo=3
        )

        return (tempo_ticket, history)

    def pause(self, tempo_ticket):
        tempo_ticket.data_termino = timezone.now()
        tempo_ticket.save()

        history = HistoricoTicket.objects.create_historico(
            ticket=tempo_ticket.ticket,
            conteudo="%s pausou o ticket." % (unicode(tempo_ticket.funcionario)),
            tipo=3
        )

        return (tempo_ticket, history)


class TempoTicket(models.Model):
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_termino = models.DateTimeField(blank=True, null=True)
    ticket = models.ForeignKey('Ticket')
    funcionario = models.ForeignKey('Funcionario')

    objects = TempoTicketManager()
# </editor-fold>
