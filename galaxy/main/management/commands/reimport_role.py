from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from galaxy.main.celerytasks.tasks import import_role
from galaxy.main.models import Role, ImportTask

User = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('role_id', nargs='+', type=int)

    def handle(self, *args, **options):
        if not options.get('role_id'):
            raise Exception("Please provide a role ID.")
        role_id = options.get('role_id')[0]
        role = Role.objects.get(id=role_id)
        last_task = ImportTask.objects.filter(role=role, state='SUCCESS').order_by('-id').first()
        task = ImportTask.objects.create(
            github_user         = role.github_user,
            github_repo         = role.github_repo,
            github_reference    = role.github_branch,
            alternate_role_name = last_task.alternate_role_name,
            role        = role,
            owner       = last_task.owner,
            state       = 'PENDING'
        )
        import_role.delay(task.id)