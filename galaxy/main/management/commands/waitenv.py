import socket
import time

from django.conf import settings
from django.core.management import base as management


def try_connect(host, port, timeout=5.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
    finally:
        s.close()


def wait_for_connection(host, port, attempts=10):
    while attempts > 0:
        try:
            return try_connect(host, port)
        except socket.error:
            pass
        time.sleep(1)
        attempts -= 1
    raise IOError('Cannot connect to {0}:{1}'.format(host, port))


class Command(management.BaseCommand):

    def handle(self, *args, **options):
        for srv in settings.WAIT_FOR:
            try:
                wait_for_connection(srv['host'], srv['port'])
            except IOError as exc:
                raise management.CommandError(exc)
