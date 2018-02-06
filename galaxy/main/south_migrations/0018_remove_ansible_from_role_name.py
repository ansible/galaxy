# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        import re
        regex=re.compile(r'^(ansible[-_.+]*)*(role[-_.+]*)*')
        for role in orm.Role.objects.all():
            try:
                if role.active:
                    new_name = regex.sub('', role.name)
                    if new_name != role.name:
                        role.name = new_name
                        role.save()
                elif role.original_name:
                    new_name = regex.sub('', role.original_name)
                    if new_name != role.original_name:
                        role.original_name = new_name
                        role.save()
            except:
                print("failed to rename role: %s/%s (id=%d)" % (role.name, role.owner.username, role.pk)) 


    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

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
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'main.platform': {
            'Meta': {'ordering': "['name', 'release']", 'object_name': 'Platform'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
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
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
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
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.CustomUser']"}),
            'platforms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'roles'", 'blank': 'True', 'to': u"orm['main.Platform']"}),
            'readme': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        u'main.roleimport': {
            'Meta': {'object_name': 'RoleImport'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'celery_task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'released': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imports'", 'to': u"orm['main.Role']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True', 'blank': 'True'}),
            'status_message': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'})
        },
        u'main.rolerating': {
            'Meta': {'unique_together': "(('owner', 'role'),)", 'object_name': 'RoleRating'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'code_quality': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
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
            'description': ('galaxy.main.fields.TruncatingCharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loose_version': ('galaxy.main.fields.LooseVersionField', [], {'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['main.Role']"})
        }
    }

    complete_apps = ['main']
    symmetrical = True
