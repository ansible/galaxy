import time

from math import ceil, floor

from github import Github

from django.conf import settings
from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError

from galaxy.main.models import Role, RefreshRoleCount
from galaxy.main.celerytasks.tasks import refresh_role_counts

class Command(BaseCommand):
    help = 'Update each role with GitHub counts'
    
    def handle(self, *args, **options):
        agg = Role.objects.filter(is_valid=True,active=True).aggregate(Max('id'))
        max_id = agg['id__max']
        size = ceil(max_id / float(len(settings.GITHUB_TASK_USERS)))
        in_list = []
        print 'Refresh Role Counts'
        # for i in range(len(settings.GITHUB_TASK_USERS)):
        i = 1
        start = size * i
        end = size * (i + 1)
        print 'User: %s' % settings.GITHUB_TASK_USERS[i]['username']
        print 'Range: %d - %d' % (start, end)
        r = RefreshRoleCount.objects.create(
            state='PENDING',
            description='User: %s Range: %s-%s' % (settings.GITHUB_TASK_USERS[i]['username'], start, end)
        )
        in_list.append(r.id)
        gh_api = Github(settings.GITHUB_TASK_USERS[i]['username'],settings.GITHUB_TASK_USERS[i]['password'])
        refresh_role_counts.delay(start, end, gh_api, r)
        print "Request submitted to Celery."

        finished = False
        started = time.time()
        while not finished:
            finished = True
            for obj in RefreshRoleCount.objects.filter(pk__in=in_list,state__not='COMPLETED'):
                if not obj.state == 'FINISHED':
                    finished = False
                else:
                    print '%s Total: %s Passed: %s Failed: %s' % (obj.description, obj.failed + obj.passed, obj.passed, obj.failed)
                    obj.state = 'COMPLETED'
                    obj.save()
            time.sleep(60)

        elapsed = time.time() - started
        hours = floor(elapsed / 3600) if elapsed > 3600 else 0
        minutes = floor((elapsed - (hours * 3600)) / 60) if (elapsed - (hours * 3600)) > 60 else 0
        seconds =  elapsed - (hours * 3600) - (minutes * 60)
        print 'Elapsed time %02d.%02d.%02d' % (hours, minutes, seconds)

