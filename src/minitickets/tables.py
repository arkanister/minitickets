# coding: utf-8
from django.core.paginator import Paginator
from django.template.defaultfilters import truncatewords

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
class TruncateWordsColumn(tables.Column):

    def __init__(self, words=5, *args, **kwargs):
        self.words = words
        super(TruncateWordsColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return truncatewords(value, self.words)


class ProdutoTable(tables.Table):

    situacao = tables_utils.BooleanColumn(verbose_name="Ativo")
    descricao = TruncateWordsColumn(words=5, attrs={
        "th": {"class": "visible-md visible-lg"},
        "td": {"class": "visible-md visible-lg"}
    })


    class Meta:
        model = Produto
        fields = ('nome', 'descricao', 'situacao')


#</editor-fold>