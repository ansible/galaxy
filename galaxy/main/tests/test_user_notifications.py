# (c) 2012-2019, Ansible
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

from django.contrib.auth import get_user_model
from django.test import TestCase
from pulpcore import constants as pulp_const
from pulpcore.app import models as pulp_models

from galaxy.main import models
from galaxy.main.celerytasks import user_notifications

UserModel = get_user_model()


class TestCollectionNotifications(TestCase):
    def setUp(self):
        self.namespace_1 = models.Namespace.objects.create(name='user_1_ns')
        self.collection_1 = models.Collection.objects.create(
            namespace=self.namespace_1, name='apache')
        self.namespace_2 = models.Namespace.objects.create(name='user_2_ns')
        self.collection_2 = models.Collection.objects.create(
            namespace=self.namespace_2, name='apache')

        # user_1 is author of collection_1
        self.user_1 = UserModel.objects.create(
            username='user_1', email='1@1.com')
        self.user_1_pref = models.UserPreferences.objects.create(
            user=self.user_1)
        self.namespace_1.owners.set([self.user_1])

        # user_2 is author of collection_2, and follows collection_1
        self.user_2 = UserModel.objects.create(
            username='user_2', email='2@2.com')
        self.user_2_pref = models.UserPreferences.objects.create(
            user=self.user_2)
        self.user_2_pref.collections_followed.set([self.collection_1])

        # user_3 follows collection_1
        self.user_3 = UserModel.objects.create(
            username='user_3', email='3@3.com')
        self.user_3_pref = models.UserPreferences.objects.create(
            user=self.user_3)
        self.user_3_pref.collections_followed.set([self.collection_1])

        # user_4 follows user_2
        self.user_4 = UserModel.objects.create(
            username='user_4', email='4@4.com')
        self.user_4_pref = models.UserPreferences.objects.create(
            user=self.user_4)
        self.user_4_pref.namespaces_followed.set([self.namespace_2])

        # user_5 follows user_2
        self.user_5 = UserModel.objects.create(
            username='user_5', email='5@5.com')
        self.user_5_pref = models.UserPreferences.objects.create(
            user=self.user_5)
        self.user_5_pref.namespaces_followed.set([self.namespace_2])

    def test_new_collection_by_author(self):
        collection = models.Collection.objects.create(
            namespace=self.namespace_2, name='nginx')
        version = models.CollectionVersion.objects.create(
            collection=collection, version='2.2.2')

        user_notifications.coll_author_release(version.pk)

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_4, self.user_5])
        assert notifications.count() == 2
        for notification in notifications:
            assert notification.message == \
                'New collection from user_2_ns: user_2_ns.nginx'
            assert notification.collection.name == collection.name

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_1, self.user_2, self.user_3])
        assert notifications.count() == 0

    def test_new_collection_notification_off(self):
        collection = models.Collection.objects.create(
            namespace=self.namespace_2, name='nginx')
        version = models.CollectionVersion.objects.create(
            collection=collection, version='2.2.2')

        self.user_5_pref.preferences['ui_notify_author_release'] = False
        self.user_5_pref.save()

        user_notifications.coll_author_release(version.pk)

        user_3_notification_count = models.UserNotification.objects.filter(
            user=self.user_5).count()
        assert user_3_notification_count == 0
        user_2_notification_count = models.UserNotification.objects.filter(
            user=self.user_4).count()
        assert user_2_notification_count == 1

    def test_new_version(self):
        version = models.CollectionVersion.objects.create(
            collection=self.collection_1, version='1.2.3')

        user_notifications.collection_new_version(version.pk)

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_2, self.user_3])
        assert notifications.count() == 2
        for notification in notifications:
            assert notification.message == \
                'New version of user_1_ns.apache: 1.2.3'
            assert notification.collection.name == self.collection_1.name

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_1, self.user_4, self.user_5])
        assert notifications.count() == 0

    def test_new_version_notification_off(self):
        version = models.CollectionVersion.objects.create(
            collection=self.collection_1, version='1.2.3')

        self.user_3_pref.preferences['ui_notify_content_release'] = False
        self.user_3_pref.save()

        user_notifications.collection_new_version(version.pk)

        user_3_notification_count = models.UserNotification.objects.filter(
            user=self.user_3).count()
        assert user_3_notification_count == 0
        user_2_notification_count = models.UserNotification.objects.filter(
            user=self.user_2).count()
        assert user_2_notification_count == 1

    def test_new_survey(self):
        user_notifications.collection_new_survey(self.collection_1.pk)

        notifications = models.UserNotification.objects.filter(
            user=self.user_1)
        assert notifications.count() == 1
        for notification in notifications:
            assert notification.message == \
                'New survey for user_1_ns.apache'
            assert notification.collection.name == self.collection_1.name

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_2, self.user_3, self.user_4, self.user_5])
        assert notifications.count() == 0

    def test_new_survey_notification_off(self):
        self.user_1_pref.preferences['ui_notify_survey'] = False
        self.user_1_pref.save()

        user_notifications.collection_new_survey(self.collection_1.pk)

        user_1_notification_count = models.UserNotification.objects.filter(
            user=self.user_1).count()
        assert user_1_notification_count == 0

    def test_import_completed(self):
        version = models.CollectionVersion.objects.create(
            collection=self.collection_1, version='1.2.4')
        pulp_task = pulp_models.Task.objects.create(
            pk=24,
            state=pulp_const.TASK_STATES.COMPLETED,
        )
        task = models.CollectionImport.objects.create(
            pk=42,
            namespace=self.namespace_1,
            name='apache',
            version='1.2.4',
            pulp_task=pulp_task,
            imported_version=version,
        )
        user_notifications.collection_import(task.pk, has_failed=False)

        notifications = models.UserNotification.objects.filter(
            user=self.user_1)
        assert notifications.count() == 1
        assert notifications[0].message == \
            'Import completed: apache 1.2.4'
        assert notifications[0].collection.name == self.collection_1.name

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_2, self.user_3, self.user_4, self.user_5])
        assert notifications.count() == 0

    def test_import_failed(self):
        version = models.CollectionVersion.objects.create(
            collection=self.collection_1, version='1.2.4')
        pulp_task = pulp_models.Task.objects.create(
            pk=24,
            state=pulp_const.TASK_STATES.FAILED,
        )
        task = models.CollectionImport.objects.create(
            pk=42,
            namespace=self.namespace_1,
            name='apache',
            version='1.2.4',
            pulp_task=pulp_task,
            imported_version=version,
        )
        user_notifications.collection_import(task.pk, has_failed=True)

        notifications = models.UserNotification.objects.filter(
            user=self.user_1)
        assert notifications.count() == 1
        assert notifications[0].message == \
            'Import failed: apache 1.2.4'

        notifications = models.UserNotification.objects.filter(
            user__in=[self.user_2, self.user_3, self.user_4, self.user_5])
        assert notifications.count() == 0
