# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Funcionario'
        db.create_table(u'minitickets_funcionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('situacao', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('cpf', self.gf('django.db.models.fields.CharField')(max_length=14, unique=True, null=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=11, unique=True, null=True)),
            ('cargo', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('nome_usuario', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'minitickets', ['Funcionario'])


    def backwards(self, orm):
        # Deleting model 'Funcionario'
        db.delete_table(u'minitickets_funcionario')


    models = {
        u'minitickets.funcionario': {
            'Meta': {'object_name': 'Funcionario'},
            'cargo': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '14', 'unique': 'True', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'nome_usuario': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '11', 'unique': 'True', 'null': 'True'}),
            'situacao': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['minitickets']