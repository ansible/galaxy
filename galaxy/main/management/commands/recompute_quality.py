"""Recomputes the Quality Score

Recomputes the quality score for a collection and all its content.

Recomputes quality score for collections which already have a
quality score. Does not reimport or relint - uses existing linter violations.

Run from inside a container, examples:

/var/lib/galaxy/venv/bin/python /galaxy/manage.py recompute_quality --help

/var/lib/galaxy/venv/bin/django-admin recompute_quality --help
"""

from datetime import datetime

import pytz
from django.core.management.base import BaseCommand

from galaxy.main.models import Repository, ImportTask
from galaxy.worker.tasks import _update_quality_score


class Command(BaseCommand):
    help = ('Recomputes quality score for collections which already have a '
            'quality score. Does not reimport or relint - '
            'uses existing linter violations.')
    repos = []

    date_range_start = datetime(2010, 1, 1)
    date_range_end = datetime.now(pytz.UTC)

    def add_arguments(self, parser):
        group_action = parser.add_mutually_exclusive_group()
        group_action.add_argument(
            '--count', action='store_true',
            help=('Get count of collections with a non-null quality '
                  'score based on --scored-* option.')
        )
        group_action.add_argument(
            '--recompute', action='store_true',
            help=('Recomputes collections with scores based '
                  'on --scored-* option. Uses existing linter violations '
                  'and latest severities, does not relint or reimport')
        )

        group_scored = parser.add_mutually_exclusive_group()
        group_scored.add_argument(
            '--scored-all', action='store_true',
            help=('Looks at collections scored at any time')
        )
        group_scored.add_argument(
            '--scored-before', nargs=1, type=str,
            help=('Looks at collections scored before given datetime, '
                  'use format 2018-10-29-23:30:00')
        )
        group_scored.add_argument(
            '--scored-after', nargs=1, type=str,
            help=('Looks at collections scored after given datetime, '
                  'use format 2018-10-29-23:30:00')
        )

    def handle(self, *args, **kwargs):
        try:
            self.set_date_range(kwargs)
        except ValueError as e:
            return self.style.ERROR(e.message)

        self.set_repos()

        if kwargs['count']:
            self.count()
        elif kwargs['recompute']:
            if not self.repos.count():
                return self.style.WARNING('0 collections to recompute')
            self.recompute()

        return self.style.SUCCESS('Successfully completed command')

    def set_date_range(self, k):
        if k['scored_before']:
            self.date_range_end = self.check_datetime(k['scored_before'][0])
        elif k['scored_after']:
            self.date_range_start = self.check_datetime(k['scored_after'][0])
            if self.date_range_start > datetime.now(pytz.UTC):
                raise ValueError('--scored-after cannot be in the future')

    def check_datetime(self, date_string):
        return datetime.strptime(date_string,
                                 '%Y-%m-%d-%H:%M:%S').replace(tzinfo=pytz.UTC)

    def set_repos(self):
        self.repos = Repository.objects.filter(
            quality_score__isnull=False,
            quality_score_date__gt=self.date_range_start,
            quality_score_date__lt=self.date_range_end,
        )

    def count(self):
        msg = "Found {} of {} collections that matched --scored-*"
        self.stdout.write(msg.format(self.repos.count(),
                                     Repository.objects.all().count()))

    def recompute(self):
        start_time = datetime.now()
        msg = ('Recomputing mean quality score for {} collections '
               'based on current severities...')
        self.stdout.write(msg.format(self.repos.count()))

        for repo in self.repos:
            self.update_from_linter_messages(repo)

        delta = (datetime.now() - start_time).total_seconds()
        msg = ('Successfully recomputed in {:.3f} seconds '
               'for {} repos, {:.3f} seconds per repo')
        self.stdout.write(msg.format(delta,
                                     self.repos.count(),
                                     delta / self.repos.count()))

    def update_from_linter_messages(self, repo):
        old_score = repo.quality_score

        latest_import_task = ImportTask.objects.filter(
            repository=repo.id).latest()

        _update_quality_score(latest_import_task)

        repo.refresh_from_db()

        msg = ("{:.1f} -> {:.1f} quality score change for import_task: {}, "
               "collection: {} {}")
        self.stdout.write(msg.format(
            old_score,
            repo.quality_score,
            latest_import_task.id,
            repo.provider_namespace.name,
            repo.name,
        ))
