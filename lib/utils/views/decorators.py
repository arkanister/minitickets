# -*- coding: utf-8 -*-

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required as django_login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator


from.types import CREATE, UPDATE, DELETE, DETAIL, LIST


def login_required(method, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """

    def wrapper(self, *args, **kwargs):

        required = getattr(self, 'login_required', True)

        if required:

            @method_decorator(django_login_required(redirect_field_name=redirect_field_name, login_url=login_url))
            def wrap(_self, *ag, **kag):
                return method(_self, *ag, **kag)

            return wrap(self, *args, **kwargs)

        return method(self, *args, **kwargs)

    return wrapper


def permission_required(method, login_url=None, raise_exception=True):

    """
    Decorator for views that checks that the user has perms, redirecting
    to the log-in page if necessary.
    """

    def wrapper(self, *args, **kwargs):
        perms = getattr(self, 'perms', [])
        model = getattr(self, 'model', None)
        view_type = getattr(self, '_TYPE', None)

        if model is not None and view_type is not None and isinstance(perms, list):
            # get a perms from a specific view
            opts = getattr(model, "_meta")
            app_name = opts.app_label.lower()
            perm = None
            if view_type == CREATE:
                perm = opts.get_add_permission()
            elif view_type == UPDATE:
                perm = opts.get_change_permission()
            elif view_type == DELETE:
                perm = opts.get_delete_permission()
            elif view_type in (DETAIL, LIST):
                perm = "view_%s" % opts.object_name.lower()

            if perm is not None:
                perms.append("%s.%s" % (app_name, perm))

        # is required if exists a perms
        required = isinstance(perms, list) and len(perms) > 0

        if required:

            def check_perms(user):

                if not user.is_authenticated() or user.has_perms(perms):
                    return True

                if raise_exception:
                    raise PermissionDenied

                return False

            @method_decorator(user_passes_test(check_perms, login_url=login_url))
            def wrap(_self, *ag, **kwg):
                return method(_self, *ag, **kwg)

            return wrap(self, *args, **kwargs)

        return method(self, *args, **kwargs)

    return wrapper