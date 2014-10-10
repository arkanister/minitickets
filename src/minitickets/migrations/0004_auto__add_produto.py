# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Produto'
        db.create_table(u'minitickets_produto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('descricao', self.gf('django.db.models.fields.TextField')()),
            ('situacao', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'minitickets', ['Produto'])


    def backwards(self, orm):
        # Deleting model 'Produto'
        db.delete_table(u'minitickets_produto')


    models = {
        u'minitickets.funcionario': {
            'Meta': {'object_name': 'Funcionario'},
            'cargo': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '14', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'nome_usuario': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'senha': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'situacao': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
        },
        u'minitickets.produto': {
            'Meta': {'object_name': 'Produto'},
            'descricao': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'situacao': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['minitickets']