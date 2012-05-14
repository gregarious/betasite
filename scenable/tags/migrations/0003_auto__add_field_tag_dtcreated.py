# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Tag.dtcreated'
        db.add_column('tags_tag', 'dtcreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 4, 9, 11, 56, 59, 176364), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Tag.dtcreated'
        db.delete_column('tags_tag', 'dtcreated')


    models = {
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'dtcreated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['tags']
