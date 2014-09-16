# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .tables import SingleTableMixin
from .list import ListView


class ModalTableSearchView(SingleTableMixin, ListView):
    table_pagination = {"per_page": 10}
    perms = None  # this ignore permissions
    search_field_name = 'search'
    ajax_required = True

    def get_template_names(self):
        opts = getattr(self.model, '_meta')
        templates = [
            '%s/modal/%s_search.html' % (opts.app_label.lower(), opts.object_name.lower()),
            'forms/modal/search.html']
        return templates

    def get(self, request, *args, **kwargs):
        # todo : define decorator
        if not request.is_ajax():
            raise PermissionDenied("This view accept only ajax request.")
        return super(ModalTableSearchView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(ModalTableSearchView, self).get_queryset()

        filters = None
        search_value = self.request.GET.get(self.search_field_name, None)

        if search_value and hasattr(self, 'fields') and \
                isinstance(self.fields, (list, tuple)) and \
                len(self.fields):
            for field in self.fields:
                f = {field + '__icontains': search_value}
                if not filters:
                    filters = Q(**f)
                else:
                    filters |= Q(**f)

        if filters is not None:
            queryset = queryset.filter(filters)
        return queryset.distinct()

    def get_row_reverse_action(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super(ModalTableSearchView, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get(self.search_field_name, None)
        return context


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