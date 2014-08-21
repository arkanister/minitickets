# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Funcionario.rg'
        db.alter_column(u'minitickets_funcionario', 'rg', self.gf('django.db.models.fields.CharField')(max_length=15, unique=True, null=True))
        # Adding unique constraint on 'Funcionario', fields ['email']
        db.create_unique(u'minitickets_funcionario', ['email'])


    def backwards(self, orm):
        # Removing unique constraint on 'Funcionario', fields ['email']
        db.delete_unique(u'minitickets_funcionario', ['email'])


        # Changing field 'Funcionario.rg'
        db.alter_column(u'minitickets_funcionario', 'rg', self.gf('django.db.models.fields.CharField')(unique=True, max_length=11, null=True))

    models = {
        u'minitickets.funcionario': {
            'Meta': {'object_name': 'Funcionario'},
            'cargo': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '14', 'unique': 'True', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'nome_usuario': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True'}),
            'senha': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'situacao': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['minitickets']