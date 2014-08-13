# -*- coding: utf-8 -*-


def page_settings_context_processor(request):
    """
    Define the defaults settings to page context.
    """
    settings = getattr(request, '_page_settings', {})
    context = {
        'TITLE': settings.get('title', None),
        'SUBTITLE': settings.get('subtitle', None),
        'BREADCRUMBS': settings.get('breadcrumbs', None),
    }
    if 'add_permission' in settings:
        context['ADD_PERM'] = settings.get('add_permission')
    if 'change_permission' in settings:
        context['CHANGE_PERM'] = settings.get('change_permission')
    if 'delete_permission' in settings:
        context['DELETE_PERM'] = settings.get('delete_permission')
    if 'view_permission' in settings:
        context['VIEW_PERM'] = settings.get('view_permission')
    return context