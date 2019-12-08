from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from galaxy.main.models import Namespace

User = get_user_model()


class Command(BaseCommand):
    help = ('For each repo, deletes all import_task_messages '
            'except for messages in latest import_task.')

    def add_arguments(self, parser):
        parser.add_argument('namespace')
        parser.add_argument('username')

    def handle(self, *args, **kwargs):
        namespace = kwargs.get('namespace')
        username = kwargs.get('username')

        try:
            _user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise Exception("User not found.")

        _namespace = Namespace.objects.create(name=namespace)
        _namespace.owners.set([_user])

        print('Namespace created successfully')
