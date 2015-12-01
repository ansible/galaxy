
from math import ceil

from github import Github

from django.conf import settings
from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError

from galaxy.main.models import Role
from galaxy.main.celerytasks.tasks import refresh_role_counts

class Command(BaseCommand):
    help = 'Update each role with counts from GitHub'
    
    def handle(self, *args, **options):

        agg = Role.objects.filter(is_valid=True,active=True).aggregate(Max('id'))
        max_id = agg['id__max']
        size = ceil(max_id / float(len(settings.GITHUB_TASK_USERS)))
        
        print 'Refresh Role Counts'
        for i in range(len(settings.GITHUB_TASK_USERS)):
            start = size * i
            end = size * (i + 1)
            print 'User: %s' % settings.GITHUB_TASK_USERS[i]['username']
            print 'Range: %d - %d' % (start, end)
            gh_api = Github(settings.GITHUB_TASK_USERS[i]['username'],settings.GITHUB_TASK_USERS[i]['password'])
            refresh_role_counts.delay(start, end, gh_api)
            print "Request submitted to Celery."