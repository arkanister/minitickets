# -*- coding: utf-8 -*-

import django_tables2 as tables

from .columns import IdColumn


def table_factory(model, columns=None, exclude=None):

    meta_attrs = {'model': model}

    fields = columns or []

    if fields:
        # force add id
        fields = ['id'] + fields if not 'id' in fields else fields

        meta_attrs.update({
            'fields': fields,
            'sequence': fields
        })

    if exclude is not None:
        meta_attrs.update({'exclude': exclude})

    meta = type('Meta', (object,), meta_attrs)
    table_class = type('ModelTable', (tables.Table,), {'Meta': meta, 'id': IdColumn()})
    return table_class