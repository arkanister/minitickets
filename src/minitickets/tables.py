# coding: utf-8

import django_tables2 as tables
from lib.utils import tables as tables_utils


# <editor-fold desc="Funcionário">
from src.minitickets.models import Funcionario


class FuncionarioTable(tables.Table):

    is_active = tables_utils.BooleanColumn(verbose_name="Ativo")

    class Meta:
        model = Funcionario
        fields = ('nome', 'email', 'cargo', 'is_active')
        orderable = False
# </editor-fold>

