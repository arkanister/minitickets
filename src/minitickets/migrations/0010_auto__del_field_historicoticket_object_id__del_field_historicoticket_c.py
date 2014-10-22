# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'HistoricoTicket.object_id'
        db.delete_column(u'minitickets_historicoticket', 'object_id')

        # Deleting field 'HistoricoTicket.content_type'
        db.delete_column(u'minitickets_historicoticket', 'content_type_id')

        # Adding field 'HistoricoTicket.criado_por'
        db.add_column(u'minitickets_historicoticket', 'criado_por',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['minitickets.Funcionario'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'HistoricoTicket.object_id'
        db.add_column(u'minitickets_historicoticket', 'object_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'HistoricoTicket.content_type'
        db.add_column(u'minitickets_historicoticket', 'content_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'HistoricoTicket.criado_por'
        db.delete_column(u'minitickets_historicoticket', 'criado_por_id')


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
        u'minitickets.historicoticket': {
            'Meta': {'ordering': "['-data_cadastro']", 'object_name': 'HistoricoTicket'},
            'conteudo': ('django.db.models.fields.TextField', [], {}),
            'criado_por': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'data_cadastro': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Ticket']"})
        },
        u'minitickets.produto': {
            'Meta': {'object_name': 'Produto'},
            'descricao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'situacao': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'minitickets.tempoticket': {
            'Meta': {'object_name': 'TempoTicket'},
            'data_inicio': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_termino': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Ticket']"})
        },
        u'minitickets.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'analista': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'analista'", 'null': 'True', 'to': u"orm['minitickets.Funcionario']"}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Cliente']"}),
            'data_abertura': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_fechamento': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {}),
            'desenvolvedor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'desenvolvedor'", 'null': 'True', 'to': u"orm['minitickets.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['minitickets.Produto']"}),
            'situacao': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'solucao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['minitickets']