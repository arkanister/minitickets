# coding: utf-8
from django.core.paginator import Paginator

import django_tables2 as tables
from lib.utils import tables as tables_utils
from src.minitickets.models import Funcionario, Produto


# <editor-fold desc="Funcionário">
class FuncionarioTable(tables.Table):

    is_active = tables_utils.BooleanColumn(verbose_name="Ativo")

    class Meta:
        model = Funcionario
        fields = ('nome', 'email', 'cargo', 'is_active')
        orderable = False
# </editor-fold>


#<editor-fold desc="Produto">
class ProdutoTable(tables.Table):

    situacao = tables_utils.BooleanColumn(verbose_name="Ativo")

    class Meta:
        model = Produto
        fields = ('nome', 'descricao', 'situacao')


#</editor-fold>