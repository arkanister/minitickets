# coding: utf-8

from django.utils.translation import ugettext as _

MAIN_NAV = [{
   "verbose_name": _('Home'),
   "action": "home",
   "icon": "home",
   "pattern": r"^/$",
}, {
        "verbose_name": u"Tickets",
        "action": "minitickets:list-ticket",
        "icon": "ticket",
        "permissions": ["minitickets.view_ticket"],
        "pattern": r"^/tickets  /",
    }, {
    "verbose_name": u"Cadastro",
    "icon": "edit",
    "submenus": [{
        "verbose_name": u"Cliente",
        "action": "minitickets:list-cliente",
        "icon": "building-o",
        "permissions": ["minitickets.view_cliente"],
        "pattern": r"^/clientes/",
    }, {
        "verbose_name": u"Produto",
        "action": "minitickets:list-produto",
        "icon": "puzzle-piece",
        "permissions": ["minitickets.view_produto"],
        "pattern": r"^/produtos/",
    }, {
        "verbose_name": u"Funcionário",
        "icon": "user",
        "action": "minitickets:list-funcionario",
        "permissions": ["minitickets.view_funcionario"],
        "pattern": r"^/funcionarios/",
    }]
}]