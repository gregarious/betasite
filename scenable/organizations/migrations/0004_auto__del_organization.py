# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('events', '0007_auto__chg_field_role_organization__chg_field_icalendarfeed_owner'),
    )

    def forwards(self, orm):
        # Deleting model 'Organization'
        db.delete_table('organizations_organization')

        # Removing M2M table for field administrators on 'Organization'
        db.delete_table('organizations_organization_administrators')

        # Removing M2M table for field establishments on 'Organization'
        db.delete_table('organizations_organization_establishments')


    def backwards(self, orm):
        # Adding model 'Organization'
        db.create_table('organizations_organization', (
            ('dtcreated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('twitter_username', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('fb_id', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('organizations', ['Organization'])

        # Adding M2M table for field administrators on 'Organization'
        db.create_table('organizations_organization_administrators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm['organizations.organization'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('organizations_organization_administrators', ['organization_id', 'user_id'])

        # Adding M2M table for field establishments on 'Organization'
        db.create_table('organizations_organization_establishments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm['organizations.organization'], null=False)),
            ('place', models.ForeignKey(orm['places.place'], null=False))
        ))
        db.create_unique('organizations_organization_establishments', ['organization_id', 'place_id'])


    models = {
        
    }

    complete_apps = ['organizations']