# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cliente'
        db.create_table(u'minitickets_cliente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome_fantasia', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('razao_social', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('cnpj', self.gf('django.db.models.fields.CharField')(unique=True, max_length=19)),
            ('inscricao_estadual', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True, blank=True)),
            ('inscricao_municipal', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True, blank=True)),
            ('nome_diretor', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('telefone', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('situacao', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
        ))
        db.send_create_signal(u'minitickets', ['Cliente'])

        # Adding M2M table for field produto on 'Cliente'
        m2m_table_name = db.shorten_name(u'minitickets_cliente_produto')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cliente', models.ForeignKey(orm[u'minitickets.cliente'], null=False)),
            ('produto', models.ForeignKey(orm[u'minitickets.produto'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cliente_id', 'produto_id'])


    def backwards(self, orm):
        # Deleting model 'Cliente'
        db.delete_table(u'minitickets_cliente')

        # Removing M2M table for field produto on 'Cliente'
        db.delete_table(db.shorten_name(u'minitickets_cliente_produto'))


    models = {
        u'minitickets.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'cnpj': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '19'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscricao_estadual': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'inscricao_municipal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'nome_diretor': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'nome_fantasia': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'produto': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['minitickets.Produto']", 'symmetrical': 'False'}),
            'razao_social': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'situacao': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'telefone': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
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