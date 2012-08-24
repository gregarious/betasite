# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeaturedImage'
        db.create_table('now_featuredimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dtcreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('now', ['FeaturedImage'])

        # Adding model 'Notice'
        db.create_table('now_notice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dtcreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=90, null=True, blank=True)),
        ))
        db.send_create_signal('now', ['Notice'])


    def backwards(self, orm):
        # Deleting model 'FeaturedImage'
        db.delete_table('now_featuredimage')

        # Deleting model 'Notice'
        db.delete_table('now_notice')


    models = {
        'now.featuredimage': {
            'Meta': {'ordering': "['-dtcreated']", 'object_name': 'FeaturedImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dtcreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'now.notice': {
            'Meta': {'ordering': "['-dtcreated']", 'object_name': 'Notice'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dtcreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['now']