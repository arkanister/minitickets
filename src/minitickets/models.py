# coding: utf-8

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Pessoa(models.Model):
    email = models.EmailField()
    situacao = models.PositiveSmallIntegerField(
        choices=(
            (1, 'Ativo'),
            (2, 'Inativo')
        ),
        default=1
    )

    def _is_active(self):
        return self.situacao == 1
    is_active = property(_is_active)

    class Meta:
        abstract = True


class PessoaFisica(Pessoa):
    nome = models.CharField(max_length=80)
    cpf = models.CharField(max_length=14, unique=True, null=True)
    rg = models.CharField(max_length=11, unique=True, null=True)

    class Meta:
        abstract = True


class Funcionario(AbstractBaseUser, PessoaFisica):
    cargo = models.PositiveSmallIntegerField(
        choices=(
            (1, u'Analista'),
            (2, u'Desenvolvedor'),
            (3, u'Gerente')
        )
    )

    nome_usuario = models.CharField(max_length=50, unique=True)

    USERNAME_FIELD = 'nome_usuario'
    REQUIRED_FIELDS = ['nome', 'email', 'cargo']

    def has_perm(self, perm, obj=None):
        return self.cargo == perm