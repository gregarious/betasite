# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # GDN: hack for mysql -- inserting the unique constraint on table creation instead of migration 0002.
        #      mysql chokes on this constraint addition for some reason. see corresponding logic in 0002.
        rows = [('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),]
        if db.backend_name == 'mysql':
            rows.append(('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True, unique=True)))
        else:
            rows.append(('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)))

        # Adding model 'Tag'
        db.create_table('tags_tag', rows)
        db.send_create_signal('tags', ['Tag'])


    def backwards(self, orm):
        
        # Deleting model 'Tag'
        db.delete_table('tags_tag')

    # GDN: see notes above
    if db.backend_name == 'mysql':
        models = {
            'tags.tag': {
                'Meta': {'object_name': 'Tag'},
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True', 'unique': 'True'})
            }
        }
    else:
        models = {
            'tags.tag': {
                'Meta': {'object_name': 'Tag'},
                'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
                'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
            }
        }

    complete_apps = ['tags']
