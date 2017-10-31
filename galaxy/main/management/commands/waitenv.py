import socket
import time
import logging

from django.conf import settings
from django.core.management import base as management

logger = logging.getLogger(__name__)


def try_connect(host, port, timeout=5.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
    finally:
        s.close()


def wait_for_connection(host, port, attempts=10):
    logger.info('Waiting on {}:{}'.format(host, port))
    while attempts > 0:
        try:
            return try_connect(host, port)
        except socket.error:
            pass
        time.sleep(6)
        attempts -= 1
    logger.error('manage.py waitenv: Failed to connect to {}:{}'.format(host, port))
    raise IOError('Cannot connect to {0}:{1}'.format(host, port))


class Command(management.BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--wait-for', action='store', dest='services', default=[], nargs='+',
                            help="Override settings.WAIT_FOR with a list of 'host:port' services to wait on")

    def handle(self, *args, **options):
        logger.info('manage.py waitenv...')
        services = options.pop('services')
        if services:
            for srv in services:
                try:
                    host, port = srv.split(':', 1)
                    wait_for_connection(host, int(port))
                except IOError as exc:
                    raise management.CommandError(exc)
            return
        for srv in settings.WAIT_FOR:
            try:
                wait_for_connection(srv['host'], srv['port'])
            except IOError as exc:
                raise management.CommandError(exc)
