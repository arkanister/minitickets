# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from django_tables2.views import SingleTableMixin as BaseSingleTableMixin

from .list import ListView
from .utils import TableActions

from ..html.icons.base import Icon
from ..tables.utils import table_factory


class SingleTableMixin(BaseSingleTableMixin):

    def get_table_class(self):
        """
        Return the class to use for the table, by view or by factory.
        """
        try:
            Table = super(SingleTableMixin, self).get_table_class()
        except ImproperlyConfigured, e:
            if hasattr(self, 'model'):
                Table = table_factory(self.model, columns=getattr(self, 'fields', None))
            else:
                raise ImproperlyConfigured(e.message)
        return Table


class SingleTableView(SingleTableMixin, ListView):
    """
    Generic view that renders a template and passes in a `.Table` object.
    """

    table_pagination = False  # {"per_page": 10}
    actions = None
    action_column_width = 80

    def __init__(self, *args, **kwargs):
        super(SingleTableView, self).__init__(*args, **kwargs)
        self.actions = TableActions() if self.actions is not False else False

    def get_actions(self):
        if self.actions is False:
            return None
        opts = getattr(self.model, '_meta')
        app_name = opts.app_label.lower()
        object_name = opts.object_name.lower()
        view_name = '%s:%s-%s'

        if self.request.user.has_perm(self.change_permission):
            self.actions.add(
                viewname=view_name % (app_name, 'change', object_name),
                verbose_name=_('Change'),
                icon=Icon('pencil', attrs={"class": 'ace-icon bigger-130'}),
                args=['pk'],
                attrs={"class": "blue tip"},
                perms=[self.change_permission]
            )

        if self.request.user.has_perm(self.delete_permission):
            self.actions.add(
                viewname=view_name % (app_name, 'delete', object_name),
                verbose_name=_('Delete'),
                icon=Icon('trash-o', attrs={"class": 'ace-icon bigger-130'}),
                args=['pk'],
                attrs={"class": "red tip"},
                perms=[self.delete_permission]
            )
        return self.actions

    def get_context_data(self, **kwargs):
        context = super(SingleTableView, self).get_context_data(**kwargs)
        if self.table_pagination is not False:
            table = kwargs.get('table', None)
            per_page_field = getattr(table, 'per_page_field', 'per_page')
            per_page = self.request.GET.get(per_page_field, None)
            per_page = per_page or self.table_pagination['per_page']
            context.update({
                "per_page": per_page
            })
        context["actions"] = self.get_actions()
        context["action_column_width"] = getattr(self, 'action_column_width', None)
        return context