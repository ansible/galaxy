# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'main_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512, db_index=True)),
        ))
        db.send_create_signal(u'main', ['Category'])

        # Adding model 'Platform'
        db.create_table(u'main_platform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('release', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'main', ['Platform'])

        # Adding model 'Role'
        db.create_table(u'main_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='roles', to=orm['accounts.CustomUser'])),
            ('github_user', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('github_repo', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('min_ansible_version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('issue_tracker_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bayesian_score', self.gf('django.db.models.fields.FloatField')(default=0.0, db_index=True)),
        ))
        db.send_create_signal(u'main', ['Role'])

        # Adding unique constraint on 'Role', fields ['owner', 'name']
        db.create_unique(u'main_role', ['owner_id', 'name'])

        # Adding M2M table for field authors on 'Role'
        m2m_table_name = db.shorten_name(u'main_role_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'main.role'], null=False)),
            ('customuser', models.ForeignKey(orm[u'accounts.customuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['role_id', 'customuser_id'])

        # Adding M2M table for field dependencies on 'Role'
        m2m_table_name = db.shorten_name(u'main_role_dependencies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_role', models.ForeignKey(orm[u'main.role'], null=False)),
            ('to_role', models.ForeignKey(orm[u'main.role'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_role_id', 'to_role_id'])

        # Adding M2M table for field categories on 'Role'
        m2m_table_name = db.shorten_name(u'main_role_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'main.role'], null=False)),
            ('category', models.ForeignKey(orm[u'main.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['role_id', 'category_id'])

        # Adding model 'RoleVersion'
        db.create_table(u'main_roleversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='versions', to=orm['main.Role'])),
            ('release_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('loose_version', self.gf('galaxy.main.fields.LooseVersionField')(db_index=True)),
        ))
        db.send_create_signal(u'main', ['RoleVersion'])

        # Adding M2M table for field platforms on 'RoleVersion'
        m2m_table_name = db.shorten_name(u'main_roleversion_platforms')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('roleversion', models.ForeignKey(orm[u'main.roleversion'], null=False)),
            ('platform', models.ForeignKey(orm[u'main.platform'], null=False))
        ))
        db.create_unique(m2m_table_name, ['roleversion_id', 'platform_id'])

        # Adding model 'RoleImport'
        db.create_table(u'main_roleimport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='imports', to=orm['main.Role'])),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(default='', max_length=100, db_index=True, blank=True)),
            ('released', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'main', ['RoleImport'])

        # Adding model 'RoleRating'
        db.create_table(u'main_rolerating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512, db_index=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ratings', to=orm['accounts.CustomUser'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ratings', to=orm['main.Role'])),
            ('ease_of_use', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('documentation', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('best_practices', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('repeatability', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('platform_support', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('overall', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('last_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, db_index=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal(u'main', ['RoleRating'])

        # Adding M2M table for field up_votes on 'RoleRating'
        m2m_table_name = db.shorten_name(u'main_rolerating_up_votes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rolerating', models.ForeignKey(orm[u'main.rolerating'], null=False)),
            ('customuser', models.ForeignKey(orm[u'accounts.customuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['rolerating_id', 'customuser_id'])

        # Adding M2M table for field down_votes on 'RoleRating'
        m2m_table_name = db.shorten_name(u'main_rolerating_down_votes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rolerating', models.ForeignKey(orm[u'main.rolerating'], null=False)),
            ('customuser', models.ForeignKey(orm[u'accounts.customuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['rolerating_id', 'customuser_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Role', fields ['owner', 'name']
        db.delete_unique(u'main_role', ['owner_id', 'name'])

        # Deleting model 'Category'
        db.delete_table(u'main_category')

        # Deleting model 'Platform'
        db.delete_table(u'main_platform')

        # Deleting model 'Role'
        db.delete_table(u'main_role')

        # Removing M2M table for field authors on 'Role'
        db.delete_table(db.shorten_name(u'main_role_authors'))

        # Removing M2M table for field dependencies on 'Role'
        db.delete_table(db.shorten_name(u'main_role_dependencies'))

        # Removing M2M table for field categories on 'Role'
        db.delete_table(db.shorten_name(u'main_role_categories'))

        # Deleting model 'RoleVersion'
        db.delete_table(u'main_roleversion')

        # Removing M2M table for field platforms on 'RoleVersion'
        db.delete_table(db.shorten_name(u'main_roleversion_platforms'))

        # Deleting model 'RoleImport'
        db.delete_table(u'main_roleimport')

        # Deleting model 'RoleRating'
        db.delete_table(u'main_rolerating')

        # Removing M2M table for field up_votes on 'RoleRating'
        db.delete_table(db.shorten_name(u'main_rolerating_up_votes'))

        # Removing M2M table for field down_votes on 'RoleRating'
        db.delete_table(db.shorten_name(u'main_rolerating_down_votes'))


    models = {
        u'accounts.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'average_score': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_index': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'})
        },
        u'main.platform': {
            'Meta': {'ordering': "['name', 'release']", 'object_name': 'Platform'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'release': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'main.role': {
            'Meta': {'unique_together': "(('owner', 'name'),)", 'object_name': 'Role'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'author_on'", 'symmetrical': 'False', 'to': u"orm['accounts.CustomUser']"}),
            'bayesian_score': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_index': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'roles'", 'blank': 'True', 'to': u"orm['main.Category']"}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['main.Role']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'github_repo': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'github_user': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'issue_tracker_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'min_ansible_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.CustomUser']"})
        },
        u'main.roleimport': {
            'Meta': {'object_name': 'RoleImport'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'celery_task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'released': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'imports'", 'to': u"orm['main.Role']"})
        },
        u'main.rolerating': {
            'Meta': {'object_name': 'RoleRating'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'best_practices': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'documentation': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'down_votes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_down_votes'", 'null': 'True', 'to': u"orm['accounts.CustomUser']"}),
            'ease_of_use': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'}),
            'overall': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'platform_support': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'repeatability': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['main.Role']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'up_votes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_up_votes'", 'null': 'True', 'to': u"orm['accounts.CustomUser']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': u"orm['accounts.CustomUser']"})
        },
        u'main.roleversion': {
            'Meta': {'ordering': "('-loose_version',)", 'object_name': 'RoleVersion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
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