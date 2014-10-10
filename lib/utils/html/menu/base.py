# -*- coding: utf-8 -*-

import re
from django.conf import settings
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.encoding import force_str, force_unicode
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from ..icons.base import Icon
from lib.utils.html.base import AttributeDict


def merge_attrs(attrs, kwargs):
    kwargs = AttributeDict(kwargs or {})
    for key, value in attrs.items():
        kwargs.attr(key, value)
    return kwargs


class BaseMenu(object):
    error_messages = {
        'type_error': "'%s' is not a %s object"
    }

    def __init__(self, request, verbose_name, icon='caret-right', attrs=None):
        self.request = request
        self.verbose_name = force_str(force_unicode(verbose_name))
        self._icon = icon if isinstance(icon, Icon) else Icon(force_str(icon), prefix='fa-', attrs={
            'class': 'fa fa-lg fa-fw'
        })
        self.attrs = attrs or {}

    class Meta:
        abstract = True

    def _get_icon(self):
        return self._icon
    icon = property(_get_icon)

    def is_active(self):
        raise NotImplementedError

    def has_perms(self):
        raise NotImplementedError

    def as_html(self):
        raise NotImplementedError

    def get_a_attrs(self, **kwargs):
        kwargs = merge_attrs(self.attrs.get('a', {}), kwargs)
        kwargs.attr('alt', self.verbose_name)
        kwargs.attr('title', force_str(self.verbose_name))
        return kwargs

    def __str__(self):
        return self.as_html()


class MenuWrapper(BaseMenu):
    def __init__(self, submenus, *args, **kwargs):
        super(MenuWrapper, self).__init__(*args, **kwargs)
        self.submenus = submenus

    def has_perms(self):
        return any([submenu.has_perms() for submenu in self.submenus])

    def is_active(self):
        return any([submenu.is_active() for submenu in self.submenus])

    def get_li_attrs(self, **kwargs):
        kwargs = merge_attrs(self.attrs.get('li', {}), kwargs)
        if self.is_active():
            kwargs.attr('class', 'active open')
        return kwargs

    def as_html(self):
        """
        Render to Menu Item

        :rtype: `~django.utils.safestring.SafeUnicode` object

        """
        if not self.has_perms():
            return ''

        li_attrs = self.get_li_attrs().as_html()
        a_attrs = self.get_a_attrs(**{'href': '#'}).as_html()
        icon = self.icon.as_html() if self.icon is not None else ''
        arrow = Icon('plus-square-o', html_tag='em', attrs={'class': ''}).as_html()
        output = u'<li {0}><a {1}>{2}<span class="menu-item-parent">{3}</span><b class="collapse-sign">{4}</b></a><ul>{5}</ul></li>'

        return format_html(
            output, li_attrs, a_attrs,
            icon, force_unicode(self.verbose_name), arrow,
            mark_safe(''.join([submenu.as_html() for submenu in self.submenus]))
        )

    def __repr__(self):
        return '<Menu: %s>' % self.verbose_name


class MenuItem(BaseMenu):
    def __init__(self, action, pattern, permissions=None, *args, **kwargs):
        super(MenuItem, self).__init__(*args, **kwargs)
        self._action = action
        self.pattern = force_str(pattern or '^')
        self.permissions = permissions or []

    def _get_action(self):
        action = self._action
        try:
            args, kwargs = [], {}
            if isinstance(action, (dict,)):
                args = action.get('args')
                kwargs = action.get('kwargs')
                action = action.get('urlconf')
            return reverse(action, args=args, kwargs=kwargs)
        except NoReverseMatch:
            return action
    action = property(_get_action)

    def is_active(self):
        """
        # TODO: comment this
        :param path:
        :return:
        """
        path = self.request.path
        debug = getattr(settings, 'DEBUG', True)
        pattern = self.pattern

        # force the base_url check
        # make a based base_url pattern
        if not debug:
            base_url = getattr(settings, 'LOGIN_REDIRECT_URL', '')
            # remove start regex and / in start and end
            base_url = ''.join(filter(
                lambda x: not x == '',
                re.sub(r'\^', '', base_url).split('/')
            ))

            # remove start regex from pattern
            pattern = re.sub('^(/|\^/|\^)', '', pattern)

            if base_url and pattern:
                pattern = r'^/%s/%s' % (base_url, pattern)
            elif not base_url:
                pattern = r'^/%s' % pattern

        return bool(re.match(pattern, path))

    def has_perm(self, perm_name):
        user = self.request.user

        if not user.is_authenticated():
            return False

        if not self.permissions:
            return True

        return user.has_perm(perm_name)

    def has_perms(self):
        return all([self.has_perm(perm_name) for perm_name in self.permissions])

    def get_li_attrs(self, **kwargs):
        kwargs = merge_attrs(self.attrs.get('li', {}), kwargs)
        if self.is_active():
            kwargs.attr('class', 'active')
        return kwargs

    def as_html(self):
        """
        Render to Menu Item

        :rtype: `~django.utils.safestring.SafeUnicode` object

        """
        if not self.has_perms():
            return ''

        li_attrs = self.get_li_attrs().as_html()
        a_attrs = self.get_a_attrs(href=self.action).as_html()
        icon = self.icon.as_html() if self.icon is not None else ''
        output = u'<li {0}><a {1}>{2}<span class="menu-item-parent">{3}</span></a></li>'

        return format_html(
            output, li_attrs, a_attrs,
            icon, force_unicode(self.verbose_name)
        )

    def __repr__(self):
        return '<Item: %s>' % self.verbose_name


def menu_factory(menus, request):
    assert isinstance(menus, (list, tuple))
    instances = []

    def builder(menu):
        menu = menu.copy()
        if "submenus" in menu:
            submenus = []
            for submenu in menu.pop('submenus'):
                submenus.append(builder(submenu))
            return MenuWrapper(request=request, submenus=submenus, **menu)
        return MenuItem(request=request, **menu)

    for menu in menus:
        instances.append(builder(menu))

    return instances