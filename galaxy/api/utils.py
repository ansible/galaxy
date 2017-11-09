# (c) 2012-2016, Ansible by Red Hat
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

# Python
import hashlib
import logging
import re
import subprocess
import sys

# Django REST Framework
from rest_framework.exceptions import ParseError, PermissionDenied

# PyCrypto
# from Crypto.Cipher import AES

__all__ = ['get_object_or_400', 'get_object_or_403', 'camelcase_to_underscore',
           'get_ansible_version', 'get_version', 'html_decode']


def get_object_or_400(klass, *args, **kwargs):
    '''
    Return a single object from the given model or queryset based on the query
    params, otherwise raise an exception that will return in a 400 response.
    '''
    from django.shortcuts import _get_queryset
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist, e:
        raise ParseError(*e.args)
    except queryset.model.MultipleObjectsReturned, e:
        raise ParseError(*e.args)


def get_object_or_403(klass, *args, **kwargs):
    '''
    Return a single object from the given model or queryset based on the query
    params, otherwise raise an exception that will return in a 403 response.
    '''
    from django.shortcuts import _get_queryset
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist, e:
        raise PermissionDenied(*e.args)
    except queryset.model.MultipleObjectsReturned, e:
        raise PermissionDenied(*e.args)


def camelcase_to_underscore(s):
    '''
    Convert CamelCase names to lowercase_with_underscore.
    '''
    s = re.sub(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', s)
    return s.lower().strip('_')


class RequireDebugTrueOrTest(logging.Filter):
    '''
    Logging filter to output when in DEBUG mode or running tests.
    '''

    def filter(self, record):
        from django.conf import settings
        return settings.DEBUG or 'test' in sys.argv


def get_ansible_version():
    '''
    Return Ansible version installed.
    '''
    try:
        proc = subprocess.Popen(['ansible', '--version'],
                                stdout=subprocess.PIPE)
        result = proc.communicate()[0]
        return result.lower().replace('ansible', '').strip()
    except:
        return 'unknown'


def get_version():
    '''
    Return galaxy version as reported by setuptools.
    '''
    from galaxy import __version__
    try:
        import pkg_resources
        return pkg_resources.require('galaxy')[0].version
    except:
        return __version__


def get_encryption_key(instance, field_name):
    '''
    Generate key for encrypted password based on instance pk and field name.
    '''
    from django.conf import settings
    h = hashlib.sha1()
    h.update(settings.SECRET_KEY)
    h.update(str(instance.pk))
    h.update(field_name)
    return h.digest()[:16]

# def encrypt_field(instance, field_name, ask=False):
#    '''
#    Return content of the given instance and field name encrypted.
#    '''
#    value = getattr(instance, field_name)
#    if not value or value.startswith('$encrypted$') or (ask and value == 'ASK'):
#        return value
#    key = get_encryption_key(instance, field_name)
#    cipher = AES.new(key, AES.MODE_ECB)
#    while len(value) % cipher.block_size != 0:
#        value += '\x00'
#    encrypted = cipher.encrypt(value)
#    b64data = base64.b64encode(encrypted)
#    return '$encrypted$%s$%s' % ('AES', b64data)
#
# def decrypt_field(instance, field_name):
#    '''
#    Return content of the given instance and field name decrypted.
#    '''
#    value = getattr(instance, field_name)
#    if not value or not value.startswith('$encrypted$'):
#        return value
#    algo, b64data = value[len('$encrypted$'):].split('$', 1)
#    if algo != 'AES':
#        raise ValueError('unsupported algorithm: %s' % algo)
#    encrypted = base64.b64decode(b64data)
#    key = get_encryption_key(instance, field_name)
#    cipher = AES.new(key, AES.MODE_ECB)
#    value = cipher.decrypt(encrypted)
#    return value.rstrip('\x00')


def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    for code in (
        ("'", '&#39;'),
        ('"', '&quot;'),
        ('>', '&gt;'),
        ('<', '&lt;'),
        ('&', '&amp;')
        ):                                 # noqa
        s = s.replace(code[1], code[0])    # noqa
    return s
