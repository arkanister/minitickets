# coding: utf-8

from django.contrib.auth.models import BaseUserManager


class FuncionarioManager(BaseUserManager):
    """ user manager, to provides create user functions """

    def create_user(self, nome_usuario, nome, email, cargo, password, **extra_fields):
        """
        Creates and saves a User with the given username,
        first_name, email and password.
        """
        if not nome_usuario:
            raise ValueError('The given username must be set')
        email = FuncionarioManager.normalize_email(email)
        user = self.model(nome_usuario=nome_usuario, email=email, nome=nome, cargo=cargo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nome_usuario, nome, email, cargo, password, **extra_fields):
        user = self.create_user(nome_usuario, nome, email, cargo, password, **extra_fields)
        user.save(using=self._db)
        return user