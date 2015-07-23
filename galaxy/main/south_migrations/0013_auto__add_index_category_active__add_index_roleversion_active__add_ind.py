# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Category', fields ['active']
        db.create_index(u'main_category', ['active'])

        # Adding index on 'RoleVersion', fields ['active']
        db.create_index(u'main_roleversion', ['active'])

        # Adding index on 'RoleRating', fields ['active']
        db.create_index(u'main_rolerating', ['active'])

        # Adding index on 'RoleImport', fields ['active']
        db.create_index(u'main_roleimport', ['active'])

        # Adding index on 'Platform', fields ['active']
        db.create_index(u'main_platform', ['active'])

        # Adding index on 'Role', fields ['is_valid']
        db.create_index(u'main_role', ['is_valid'])

        # Adding index on 'Role', fields ['active']
        db.create_index(u'main_role', ['active'])


    def backwards(self, orm):
        # Removing index on 'Role', fields ['active']
        db.delete_index(u'main_role', ['active'])

        # Removing index on 'Role', fields ['is_valid']
        db.delete_index(u'main_role', ['is_valid'])

        # Removing index on 'Platform', fields ['active']
        db.delete_index(u'main_platform', ['active'])

        # Removing index on 'RoleImport', fields ['active']
        db.delete_index(u'main_roleimport', ['active'])

        # Removing index on 'RoleRating', fields ['active']
        db.delete_index(u'main_rolerating', ['active'])

        # Removing index on 'RoleVersion', fields ['active']
        db.delete_index(u'main_roleversion', ['active'])

        # Removing index on 'Category', fields ['active']
        db.delete_index(u'main_category', ['active'])


    models = {
        u'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'karma': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'})
        },
        u'main.platform': {
            'Meta': {'ordering': "['name', 'release']", 'object_name': 'Platform'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'release': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'main.role': {
            'Meta': {'unique_together': "(('owner', 'name'),)", 'object_name': 'Role'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'author_on'", 'symmetrical': 'False', 'to': u"orm['accounts.CustomUser']"}),
            'bayesian_score': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_index': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'roles'", 'blank': 'True', 'to': u"orm['main.Category']"}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['main.Role']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'github_repo': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'github_user': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'issue_tracker_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'min_ansible_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.CustomUser']"}),
            'readme': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        u'main.roleimport': {
            'Meta': {'object_name': 'RoleImport'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'celery_task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'released': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imports'", 'to': u"orm['main.Role']"})
        },
        u'main.rolerating': {
            'Meta': {'unique_together': "(('owner', 'role'),)", 'object_name': 'RoleRating'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'code_quality': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'documentation': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'down_votes': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'user_down_votes'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['accounts.CustomUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['accounts.CustomUser']"}),
            'reliability': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['main.Role']"}),
            'score': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_index': 'True'}),
            'up_votes': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'related_name': "'user_up_votes'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['accounts.CustomUser']"}),
            'wow_factor': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        u'main.roleversion': {
            'Meta': {'ordering': "('-loose_version',)", 'object_name': 'RoleVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loose_version': ('galaxy.main.fields.LooseVersionField', [], {'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'platforms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['main.Platform']"}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['main.Role']"})
        }
    }

    complete_apps = ['main']