# coding: utf-8

import django_tables2 as tables

from lib.utils import tables as tables_utils
from src.minitickets.models import Funcionario, Produto


# <editor-fold desc="Funcionário">
class FuncionarioTable(tables.Table):

    id = tables_utils.IdColumn()
    is_active = tables_utils.BooleanColumn(verbose_name="Ativo")

    class Meta:
        model = Funcionario
        fields = sequence = ('id', 'nome', 'email', 'cargo', 'is_active')

        orderable = False

# </editor-fold>


#<editor-fold desc="Produto">
class ProdutoTable(tables.Table):
    id = tables_utils.IdColumn()
    situacao = tables_utils.BooleanColumn(verbose_name="Ativo")
    descricao = tables_utils.TruncateCharsColumn(attrs={
        "th": {"class": "visible-md visible-lg"},
        "td": {"class": "visible-md visible-lg"}
    })

    class Meta:
        model = Produto
        fields = sequence = ('id', 'nome', 'descricao', 'situacao')
        orderable = False
#</editor-fold>
