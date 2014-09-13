# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ticket'
        db.create_table(u'minitickets_ticket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cliente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['minitickets.Cliente'])),
            ('produto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['minitickets.Produto'])),
            ('analista', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['minitickets.Funcionario'], null=True, blank=True)),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('descricao', self.gf('django.db.models.fields.TextField')()),
            ('tipo', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('data_abertura', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('situacao', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'minitickets', ['Ticket'])

        # Removing M2M table for field produto on 'Cliente'
        db.delete_table(db.shorten_name(u'minitickets_cliente_produto'))

        # Adding M2M table for field produtos on 'Cliente'
        m2m_table_name = db.shorten_name(u'minitickets_cliente_produtos')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cliente', models.ForeignKey(orm[u'minitickets.cliente'], null=False)),
            ('produto', models.ForeignKey(orm[u'minitickets.produto'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cliente_id', 'produto_id'])


        # Changing field 'Cliente.cnpj'
        db.alter_column(u'minitickets_cliente', 'cnpj', self.gf('django.db.models.fields.CharField')(unique=True, max_length=18))

        # Changing field 'Cliente.nome_fantasia'
        db.alter_column(u'minitickets_cliente', 'nome_fantasia', self.gf('django.db.models.fields.CharField')(max_length=80, null=True))

        # Changing field 'Cliente.telefone'
        db.alter_column(u'minitickets_cliente', 'telefone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True))

        # Changing field 'Produto.descricao'
        db.alter_column(u'minitickets_produto', 'descricao', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting model 'Ticket'
        db.delete_table(u'minitickets_ticket')

        # Adding M2M table for field produto on 'Cliente'
        m2m_table_name = db.shorten_name(u'minitickets_cliente_produto')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cliente', models.ForeignKey(orm[u'minitickets.cliente'], null=False)),
            ('produto', models.ForeignKey(orm[u'minitickets.produto'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cliente_id', 'produto_id'])

        # Removing M2M table for field produtos on 'Cliente'
        db.delete_table(db.shorten_name(u'minitickets_cliente_produtos'))


        # Changing field 'Cliente.cnpj'
        db.alter_column(u'minitickets_cliente', 'cnpj', self.gf('django.db.models.fields.CharField')(max_length=19, unique=True))

        # Changing field 'Cliente.nome_fantasia'
        db.alter_column(u'minitickets_cliente', 'nome_fantasia', self.gf('django.db.models.fields.CharField')(default='Nome Fantasia', max_length=80))
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Cliente.telefone'
        db.alter_column(u'minitickets_cliente', 'telefone', self.gf('django.db.models.fields.CharField')(default='(43) 3333-3333', max_length=15))
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Produto.descricao'
        db.alter_column(u'minitickets_produto', 'descricao', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        u'minitickets.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'cnpj': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '18'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inscricao_estadual': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'inscricao_municipal': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'nome_diretor': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'nome_fantasia': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'produtos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['minitickets.Produto']", 'null': 'True', 'blank': 'True'}),
            'razao_social': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'situacao': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'telefone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'})
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
            'descricao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'situacao': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'minitickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'analista': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Cliente']"}),
            'data_abertura': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Produto']"}),
            'situacao': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'tipo': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['minitickets']