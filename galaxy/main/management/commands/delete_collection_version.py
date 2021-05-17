from django.core.management.base import BaseCommand
from dynaconf.contrib import django_dynaconf  # noqa

from pulpcore.app.models import Repository, RepositoryVersion
from pulpcore.app.tasks import orphan_cleanup
from pulpcore.app.tasks.repository import add_and_remove

from galaxy.common.tasking import create_task


class Command(BaseCommand):
    help = ("Remove CollectionVersion's from Repository and database. "
            "For use when Collection has subset of its CollectionVersion to "
            "be removed, if you want to remove all CollectionVersion for a "
            "Collection, more analysis should be done. Call bump_repo_version "
            "with list of CollectionVersion ids then "
            "after task is complete call delete_old_repo_versions, "
            "then call run_orphan_cleanup to delete CollectionVersion "
            "not part of any RepositoryVersion.")

    def add_arguments(self, parser):
        parser.add_argument(
            'subcommand',
            type=str,
            help='Options: bump_repo_version, delete_old_repo_versions, '
                 'run_orphan_cleanup')
        parser.add_argument(
            '--collection-version-ids',
            nargs='+',
            type=int,
            help='CollectionVersion ids to delete, needed '
                 'for "bump_repo_version" subcommand')

    def handle(self, *args, **kwargs):
        assert Repository.objects.all().count() == 1, 'Expected 1 repository'
        repo = Repository.objects.get()

        # Resources to lock when running tasks. Need path component of the
        # resource URI of repository, but 'repositories-detail' view is not
        # exposed within galaxy and pulpcore.tasking.util.get_url()
        # reverse lookup causes django.urls.exceptions.NoReverseMatch error.
        # resources = [repo]
        resources = []

        subcommand = kwargs.get('subcommand')
        if subcommand == 'bump_repo_version':
            collection_versions = kwargs.get('collection_version_ids')
            self._bump_repo_version(repo, resources, collection_versions)
        elif subcommand == 'delete_old_repo_versions':
            self._delete_old_repo_versions(repo, resources)
        elif subcommand == 'run_orphan_cleanup':
            self._run_orphan_cleanup(resources)
        else:
            exit('Unknown subcommand')

    def _bump_repo_version(self, repo, resources, collection_versions):
        """Create new RepositoryVersion without specific CollectionVersion."""
        params = {
            'repository_pk': repo.pk,
            'add_content_units': [],
            'remove_content_units': collection_versions,
        }
        task = create_task(
            add_and_remove,
            params=params,
            resources=resources,
            task_args={})
        print(f'task created: {task}')

    def _delete_old_repo_versions(self, repo, resources):
        """ Delete all but latest RepositoryVersion."""
        latest_repo_version = \
            RepositoryVersion.objects.filter(repository=repo).latest()
        repo_versions_to_delete = [
            rv.pk for
            rv in RepositoryVersion.objects.exclude(pk=latest_repo_version.pk)]
        for rv_pk in repo_versions_to_delete:
            RepositoryVersion.objects.get(pk=rv_pk).delete()

    def _run_orphan_cleanup(self, resources):
        """ Run orphan_cleanup to delete all CollectionVersions that are
            not part of any RepositoryVersion."""
        task = create_task(
            orphan_cleanup,
            params={},
            resources=resources,
            task_args={})
        print(f'task created: {task}')
