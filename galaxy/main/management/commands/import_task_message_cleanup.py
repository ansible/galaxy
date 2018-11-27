from django.core.management.base import BaseCommand

from galaxy.main.models import Repository, ImportTaskMessage


class Command(BaseCommand):
    help = ('For each repo, deletes all import_task_messages '
            'except for messages in latest import_task.')

    def handle(self, *args, **kwargs):
        total_msg_to_delete = 0
        total_delete_calls = 0

        repos = Repository.objects.all()
        for repo in repos:
            tasks_non_latest = repo.import_tasks.order_by('-id')[1:]

            messages_non_latest = ImportTaskMessage.objects.filter(
                task__in=tasks_non_latest
            )

            total_msg_to_delete += messages_non_latest.count()
            total_delete_calls += 1

            messages_non_latest.delete()

        print('total_msg_to_delete', total_msg_to_delete)
        print('total_delete_calls', total_delete_calls)
