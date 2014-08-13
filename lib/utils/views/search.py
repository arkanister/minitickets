# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .tables import SingleTableMixin
from .list import ListView


class SimpleSearchAjaxView(SingleTableMixin, ListView):
    template_name = "defaults/modal/search.html"
    table_pagination = {"per_page": 10}
    perms = None  # this ignore permissions
    search_field_name = 'search'

    def get(self, request, *args, **kwargs):
        # todo : define decorator
        if not request.is_ajax():
            raise PermissionDenied("This view accept only ajax request.")
        return super(SimpleSearchAjaxView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(SimpleSearchAjaxView, self).get_queryset()

        filters = None
        search_value = self.request.GET.get(self.search_field_name, None)

        if search_value and hasattr(self, 'fields') and \
                isinstance(self.fields, (list, tuple)) and \
                len(self.fields):
            for field in self.fields:
                if not filters:
                    f = {field + '__icontains': search_value}
                    filters = Q(**f)
                    continue
                filters |= Q(**f)

        if filters is not None:
            try:
                queryset = queryset.filter(filters)
            except:
                pass
        return queryset.distinct()

    def get_reverse_func(self):
        def simple_reverse(obj):
            viewname = getattr(self, 'reverse_view_name', None)
            return reverse(viewname)
        return simple_reverse

    def get_table_class(self):
        table = super(SimpleSearchAjaxView, self).get_table_class()
        table.reverse_func = self.get_reverse_func()
        return table


'''from .tables import SingleTableView


class SimpleSearchMixin(object):

    search_fields = None
    search_field_name = None

    def get_queryset(self):
        queryset = super(SimpleSearchMixin, self).get_queryset()

        search_value = self.request.GET.get(self.search_field_name or 'search', None)

        if search_value is not None:

            search_fields = self.search_fields

            if not self.search_fields:
                opts = getattr(self.model, '_meta')
                search_fields = opts.get_all_field_names()

            _filter = Q()
            for field_name in search_fields:
                value = search_value
                filter_suffix = "__icontains"

                try:
                    field = opts.get_field(field_name)
                    field_type = field.get_internal_type()

                    if field_type in ("DateField", "DateTimeField"):
                        filter_suffix = '__startswith'
                        if re.match(r'^(\d{2}/){2}\d{4}', value):
                            value = datetime.strptime(value, "%d/%m/%Y").date
                        elif re.match(r'^(\d{2}/){2}\d{2}', value):
                            value = datetime.strptime(value, "%d/%m/%y").date
                        else:
                            continue
                    elif field_type in ("IntegerField", "AutoField"):
                        filter_suffix = ''
                        value = int(value)
                    elif field_type in ('ManyToManyField', 'ManyToOneField', 'ForeignKeyField'):
                        continue
                except Exception:
                    continue

                _filter |= Q(**{field_name + filter_suffix: value})

            queryset = queryset.filter(_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SimpleSearchMixin, self).get_context_data(**kwargs)

        search_value = self.request.GET.get(self.search_field_name or 'search', None)
        if search_value is not None:
            context.update({"search": search_value})

        return context


class SingleTableSearchView(SimpleSearchMixin, SingleTableView):

    """
    A view with a search table enabled.
    """

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)'''