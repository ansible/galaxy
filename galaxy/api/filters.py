# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (c) 2013 AnsibleWorks, Inc.
# All Rights Reserved.

# Python
import re

# Django
from django.core.exceptions import FieldError, ValidationError, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel

# Django REST Framework
from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend

# drf-haystack
from drf_haystack.filters import HaystackFilter

# Galaxy
from galaxy.main.models import UserAlias

GalaxyUser = get_user_model()

class ActiveOnlyBackend(BaseFilterBackend):
    '''
    Filter to show only objects where is_active/active is True.
    '''

    def filter_queryset(self, request, queryset, view):
        for field in queryset.model._meta.fields:
            if field.name == 'is_active':
                queryset = queryset.filter(is_active=True)
            elif field.name == 'active':
                queryset = queryset.filter(active=True)
        return queryset

class FieldLookupBackend(BaseFilterBackend):
    '''
    Filter using field lookups provided via query string parameters.
    '''

    RESERVED_NAMES = ('page', 'page_size', 'format', 'order', 'order_by',
                      'search')

    SUPPORTED_LOOKUPS = ('exact', 'iexact', 'contains', 'icontains',
                         'startswith', 'istartswith', 'endswith', 'iendswith',
                         'regex', 'iregex', 'gt', 'gte', 'lt', 'lte', 'in',
                         'isnull')

    def get_field_from_lookup(self, model, lookup):
        field = None
        parts = lookup.split('__')
        if parts and parts[-1] not in self.SUPPORTED_LOOKUPS:
            parts.append('exact')
        # FIXME: Could build up a list of models used across relationships, use
        # those lookups combined with request.user.get_queryset(Model) to make
        # sure user cannot query using objects he could not view.
        for n, name in enumerate(parts[:-1]):
            if name == 'pk':
                field = model._meta.pk
            else:
                field = model._meta.get_field_by_name(name)[0]
            if n < (len(parts) - 2):
                if getattr(field, 'rel', None):
                    model = field.rel.to
                else:
                    model = field.model
        return field

    def to_python_boolean(self, value, allow_none=False):
        value = unicode(value)
        if value.lower() in ('true', '1'):
            return True
        elif value.lower() in ('false', '0'):
            return False
        elif allow_none and value.lower() in ('none', 'null'):
            return None
        else:
            raise ValueError(u'Unable to convert "%s" to boolean' % unicode(value))

    def to_python_related(self, value):
        value = unicode(value)
        if value.lower() in ('none', 'null'):
            return None
        else:
            return int(value)

    def value_to_python_for_field(self, field, value):
        if isinstance(field, models.NullBooleanField):
            return self.to_python_boolean(value, allow_none=True)
        elif isinstance(field, models.BooleanField):
            return self.to_python_boolean(value)
        elif isinstance(field, ForeignObjectRel):
            return self.to_python_related(value)
        else:
            return field.to_python(value)

    def value_to_python(self, model, lookup, value):
        field = self.get_field_from_lookup(model, lookup)
        if lookup.endswith('__isnull'):
            value = self.to_python_boolean(value)
        elif lookup.endswith('__in'):
            items = []
            for item in value.split(','):
                items.append(self.value_to_python_for_field(field, item))
            value = items
        elif lookup.endswith('__regex') or lookup.endswith('__iregex'):
            try:
                re.compile(value)
            except re.error, e:
                raise ValueError(e.args[0])
            return value
        else:
            value = self.value_to_python_for_field(field, value)
        return value

    def filter_queryset(self, request, queryset, view):
        # this is a hack to allow aliases on user names when
        # filtering on owner__username. QUERY_PARAMS is supposed
        # to be an alias for GET, however they appear to be distinct
        # objects internally, and since there is no setter for the
        # QUERY_PARAMS version we use GET instead directly
        if 'owner__username' in request.GET:
            try:
                # try and lookup the user first, to see if it exists
                GalaxyUser.objects.get(username=request.GET['owner__username'])
            except ObjectDoesNotExist, e:
                # if not, check to see if there's an alias for it
                try:
                    alias_obj = UserAlias.objects.get(alias_name=request.GET['owner__username'])
                    # and override that query parameter with the actual username
                    qp = request.GET.copy()
                    qp['owner__username'] = alias_obj.alias_of.username
                    # Again, we use GET here because QUERY_PARAMS has no
                    # setter function, so trying to do so here results in
                    # an error. Furthermore, even when GET is set to the
                    # new QueryDict object, QUERY_PARAMS remains unchanged,
                    # meaning we have to use GET everywhere to ensure the
                    # same object is being used with the overridden param.
                    # This may be fixed in later DRF versions?
                    request.GET = qp
                except Exception, e:
                    # if not, we don't care, the later filtering
                    # means an empty set will be returned for this
                    pass

        try:
            # Apply filters specified via GET/QUERY_PARAMS. Each
            # entry in the lists below is (negate, field, value).
            and_filters = []
            or_filters = []
            chain_filters = []
            for key, values in request.GET.lists():
                if key in self.RESERVED_NAMES:
                    continue

                # Custom __int filter suffix (internal use only).
                q_int = False
                if key.endswith('__int'):
                    key = key[:-5]
                    q_int = True
                # Custom chained filter
                q_chain = False
                if key.startswith('chain__'):
                    key = key[7:]
                    q_chain = True
                # Custom or__ filter prefix (or__ can precede not__).
                q_or = False
                if key.startswith('or__'):
                    key = key[4:]
                    q_or = True
                # Custom not__ filter prefix.
                q_not = False
                if key.startswith('not__'):
                    key = key[5:]
                    q_not = True

                # Convert value(s) to python and add to the appropriate list.
                for value in values:
                    if q_int:
                        value = int(value)
                    value = self.value_to_python(queryset.model, key, value)
                    if q_chain:
                        chain_filters.append((q_not, key, value))
                    elif q_or:
                        or_filters.append((q_not, key, value))
                    else:
                        and_filters.append((q_not, key, value))

            # Now build Q objects for database query filter.
            if and_filters or or_filters or chain_filters:
                args = []
                for n, k, v in and_filters:
                    if n:
                        args.append(~Q(**{k:v}))
                    else:
                        args.append(Q(**{k:v}))
                if or_filters:
                    q = Q()
                    for n,k,v in or_filters:
                        if n:
                            q |= ~Q(**{k:v})
                        else:
                            q |= Q(**{k:v})
                    args.append(q)
                queryset = queryset.filter(*args)
                for n,k,v in chain_filters:
                    if n:
                        q = ~Q(**{k:v})
                    else:
                        q = Q(**{k:v})
                    queryset = queryset.filter(q)
            return queryset.distinct()
        except (FieldError, FieldDoesNotExist, ValueError), e:
            raise ParseError(e.args[0])
        except ValidationError, e:
            raise ParseError(e.messages)

class OrderByBackend(BaseFilterBackend):
    '''
    Filter to apply ordering based on query string parameters.
    '''

    def filter_queryset(self, request, queryset, view):
        try:
            order_by = None
            for key, value in request.GET.items():
                if key in ('order', 'order_by'):
                    order_by = value
                    if ',' in value:
                        order_by = value.split(',')
                    else:
                        order_by = (value,)
            if order_by:
                queryset = queryset.order_by(*order_by)
                # Fetch the first result to run the query, otherwise we don't
                # always catch the FieldError for invalid field names.
                try:
                    queryset[0]
                except IndexError:
                    pass
            return queryset
        except FieldError, e:
            # Return a 400 for invalid field names.
            raise ParseError(*e.args)

class HaystackFilter(HaystackFilter):
    def filter_queryset(self, request, queryset, view):
        qs = super(HaystackFilter, self).filter_queryset(request, queryset, view)
        try:
            order_by = None
            for key, value in request.GET.items():
                if key in ('order', 'order_by'):
                    order_by = value
                    if ',' in value:
                        order_by = value.split(',')
                    else:
                        order_by = (value,)
            if order_by:
                qs = qs.order_by(*order_by)
            return qs
        except FieldError, e:
            # Return a 400 for invalid field names.
            raise ParseError(*e.args)
