# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Tag', fields ['name']
        # GDN: FOR non-mysql ONLY! See notes in 0001.
        if db.backend_name != 'mysql':
            db.create_unique('tags_tag', ['name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Tag', fields ['name']
        # GDN: FOR non-mysql ONLY! See notes in 0001.
        if db.backend_name != 'mysql':
            db.delete_unique('tags_tag', ['name'])


    models = {
        'tags.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['tags']
