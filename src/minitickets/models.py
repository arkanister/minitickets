# coding: utf-8

import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import simplejson as json
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
    descricao = models.TextField()
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
    nome_fantasia = models.CharField(max_length=80)
    razao_social = models.CharField(max_length=80, unique=True)
    cnpj = models.CharField(max_length=19, unique=True)
    inscricao_estadual = models.CharField(max_length=20, unique=True, blank=True, null=True)
    inscricao_municipal = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nome_diretor = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    produto = models.ManyToManyField('Produto')
    situacao = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Ativo'),
            (2, 'Inativo')
        ),
        default=1
    )
# </editor-fold>