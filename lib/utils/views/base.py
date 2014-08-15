# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.encoding import smart_unicode, force_str

from django.utils.html import strip_tags
from django.views.generic.base import View as DjangoView, TemplateResponseMixin, \
    ContextMixin
from django.utils.translation import ugettext as _

from .utils import S, Breadcrumbs, Messages
from .decorators import login_required as decorator_login_required, permission_required

from ..html import Icon


class SmartView(DjangoView):
    """
    Uma view generica com algumas melhorias
    no que diz respeito ao padrão utilizado na renderização
    das páginas no sistema.
    Ela inclui algumas funcionalidades como breadcrumbs, mensagens,
    login required, permission required e um contexto baseado no modelo.
    """

    title = None
    subtitle = None

    pluralize_title = False  # Utilizado para retornar um title pluralizado.

    breadcrumbs = None
    messages = None

    login_required = True

    @decorator_login_required
    @permission_required
    def dispatch(self, request, *args, **kwargs):

        # define breadcrumbs adapter
        if self.breadcrumbs is not False:
            self.breadcrumbs = Breadcrumbs()

        # define de messages adapter
        self.messages = Messages(request=request)

        # define permissions
        if hasattr(self, 'model'):
            # include a defaults permissions
            opts = getattr(self.model, '_meta')
            perm_str = opts.app_label.lower() + '.%s'
            setattr(self, 'add_permission', perm_str % opts.get_add_permission())
            setattr(self, 'change_permission', perm_str % opts.get_change_permission())
            setattr(self, 'delete_permission', perm_str % opts.get_delete_permission())
            setattr(self, 'view_permission', perm_str % (opts.object_name.lower() + '_' + 'view'))

        response = super(SmartView, self).dispatch(request, *args, **kwargs)

        # register a smart page settings
        request._page_settings = {
            'title': self.get_title(),
            'subtitle': self.get_subtitle()
        }

        if self.has_breadcrumbs():
            request._page_settings['breadcrumbs'] = self.get_breadcrumbs()

        if hasattr(self, 'model'):
            request._page_settings['add_permission'] = getattr(self, 'add_permission')
            request._page_settings['change_permission'] = getattr(self, 'change_permission')
            request._page_settings['delete_permission'] = getattr(self, 'delete_permission')
            request._page_settings['view_permission'] = getattr(self, 'view_permission')

        return response

    def get_breadcrumbs(self):
        """
        Retorna os breadcrumbs da página.
        para desabilitar os breadcrumbs basta definir a variável
        breadcrumbs como `False`.
        """
        if self.breadcrumbs is False:
            return None
        self.breadcrumbs.add(_('Home'), url=getattr(settings, 'LOGIN_REDIRECT_URL'),
                             icon=Icon('home', attrs={"class": "home-icon"}))
        self.breadcrumbs.add(strip_tags(self.get_title()))
        return self.breadcrumbs

    def has_breadcrumbs(self):
        """
        Verifica se os breadcrumbs estão habilitados para a página.
        """
        return self.breadcrumbs is not False

    def get_title(self):
        """ Retorna o titulo da página. """
        instance = getattr(self, 'object', None)
        model = getattr(self, 'model', None)

        if model is None and instance is not None:
            model = instance.__class__

        title = self.title

        if title is None and model is not None:
            title = "[verbose_name]" if not self.pluralize_title else "[verbose_name_plural]"

        title = force_str(title)

        if title is not None:
            if instance is None and model is not None:
                instance = {
                    'verbose_name': model._meta.verbose_name,
                    'verbose_name_plural': model._meta.verbose_name_plural
                }
                title = S(title).compile(context=instance, prettify=True)
            elif hasattr(self, 'object'):
                title = S(title).compile(context=instance, prettify=True)

        return title

    def get_message(self, status):
        """
        Resolve message by status
        :param status:
        :return:
        """
        message = getattr(self, '%s_message' % status, None)

        if not message:
            default_messages = getattr(self, '_default_template_messages', {})
            message = default_messages.get(status, '')

        message = force_str(message)
        instance = getattr(self, 'object', None)
        return S(message).compile(instance=instance)

    def get_subtitle(self):
        """ retorna o subtitulo da página """
        if self.subtitle:
            subtitle = force_str(self.subtitle)
            return S(subtitle or '').compile(prettify=True)
        return None


class TemplateSmartView(TemplateResponseMixin, ContextMixin, SmartView):
    """ View para renderizar um template simples. """

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())