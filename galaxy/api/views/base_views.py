# (c) 2012-2018, Ansible by Red Hat
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

import inspect
import logging
import six

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.request import clone_request
from rest_framework.response import Response
from rest_framework import views

from galaxy.api.access import check_user_access
from galaxy.api.utils import camelcase_to_underscore


# FIXME: machinery for auto-adding audit trail logs to all CREATE/EDITS
__all__ = [
    'APIView', 'GenericAPIView', 'ListAPIView', 'ListCreateAPIView',
    'SubListAPIView', 'RetrieveAPIView',
    'RetrieveUpdateAPIView', 'RetrieveUpdateDestroyAPIView',
]

logger = logging.getLogger('galaxy.api.base_views')


def get_view_description(cls, html=False):
    """
    Wrapper around REST framework get_view_description() to support
    get_description() method and view_description property on a view class.
    """
    if hasattr(cls, 'get_description') and callable(cls.get_description):
        desc = cls().get_description(html=html)
        cls = type(cls.__name__, (object,), {'__doc__': desc})
    elif hasattr(cls, 'view_description'):
        if callable(cls.view_description):
            view_desc = cls.view_description()
        else:
            view_desc = cls.view_description
        cls = type(cls.__name__, (object,), {'__doc__': view_desc})
    desc = views.get_view_description(cls, html=html)
    if html:
        desc = '<div class="description">%s</div>' % desc
    return mark_safe(desc)


class APIView(views.APIView):

    def get_authenticate_header(self, request):
        """
        Determine the WWW-Authenticate header to use for 401 responses.  Try to
        use the request header as an indication for which authentication method
        was attempted.
        """
        for authenticator in self.get_authenticators():
            resp_hdr = authenticator.authenticate_header(request)
            if not resp_hdr:
                continue
            req_hdr = get_authorization_header(request)
            if not req_hdr:
                continue
            if (resp_hdr.split()[0] and
                    resp_hdr.split()[0] == req_hdr.split()[0]):
                return resp_hdr
        return super(APIView, self).get_authenticate_header(request)

    def get_description_context(self):
        return {
            'docstring': type(self).__doc__ or '',
            'new_in_13': getattr(self, 'new_in_13', False),
            'new_in_14': getattr(self, 'new_in_14', False),
        }

    def get_description(self, html=False):
        template_list = []
        for klass in inspect.getmro(type(self)):
            template_basename = camelcase_to_underscore(klass.__name__)
            template_list.append('main/%s.md' % template_basename)
        context = self.get_description_context()
        return render_to_string(template_list, context)


class GenericAPIView(generics.GenericAPIView, APIView):
    """Base class for all model-based views.

    Subclasses should define:
      model = ModelClass
      serializer_class = SerializerClass
    """

    def get_queryset(self):
        qs = self.model.objects.all().distinct()
        return qs

    def get_description_context(self):
        # Set instance attributes needed to get serializer metadata.
        if not hasattr(self, 'request'):
            self.request = None
        if not hasattr(self, 'format_kwarg'):
            self.format_kwarg = 'format'
        d = super(GenericAPIView, self).get_description_context()
        d.update({
            'model_verbose_name':
                six.text_type(self.model._meta.verbose_name),
            'model_verbose_name_plural':
                six.text_type(self.model._meta.verbose_name_plural),
            'serializer_fields': self.get_serializer().metadata(),
        })
        return d

    def metadata(self, request):
        """
        Add field information for GET requests (so field names/labels are
        available even when we can't POST/PUT).
        """
        ret = super(GenericAPIView, self).metadata(request)
        actions = ret.get('actions', {})
        # Remove read only fields from PUT/POST data.
        for method in ('POST', 'PUT'):
            fields = actions.get(method, {})
            for field, meta in fields.items():
                if not isinstance(meta, dict):
                    continue
                if meta.get('read_only', False):
                    fields.pop(field)
        if 'GET' in self.allowed_methods:
            cloned_request = clone_request(request, 'GET')
            try:
                # Test global permissions
                self.check_permissions(cloned_request)
                # Test object permissions
                if hasattr(self, 'retrieve'):
                    try:
                        self.get_object()
                    except Http404:
                        # Http404 should be acceptable and the serializer
                        # metadata should be populated. Except this so the
                        # outer "else" clause of the try-except-else block
                        # will be executed.
                        pass
            except Exception:
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that
                # should be supplied.
                serializer = self.get_serializer()
                actions['GET'] = serializer.metadata()
        if actions:
            ret['actions'] = actions
        if getattr(self, 'search_fields', None):
            ret['search_fields'] = self.search_fields
        return ret


class ListAPIView(generics.ListAPIView, GenericAPIView):
    """Base class for a read-only list view."""

    def get_description_context(self):
        opts = self.model._meta
        if 'username' in opts.get_all_field_names():
            order_field = 'username'
        else:
            order_field = 'name'
        d = super(ListAPIView, self).get_description_context()
        d.update({
            'order_field': order_field,
        })
        return d

    @property
    def search_fields(self):
        fields = []
        for field in self.model._meta.fields:
            if field.name in ('username', 'first_name', 'last_name', 'email',
                              'name', 'description', 'email'):
                fields.append(field.name)
        return fields

    def make_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListCreateAPIView(ListAPIView, generics.ListCreateAPIView):
    """Base class for a list view that allows creating new objects."""

    def pre_save(self, obj):
        if hasattr(self.model, 'owner'):
            obj['owner_id'] = self.request.user.id


class SubListAPIView(ListAPIView):
    """Base class for a read-only sublist view.

    Subclasses should define at least:
      model = ModelClass
      serializer_class = SerializerClass
      parent_model = ModelClass
      relationship = 'rel_name_from_parent_to_model'
    And optionally (user must have given access permission on parent object
    to view sublist):
      parent_access = 'read'
    """

    def get_description_context(self):
        d = super(SubListAPIView, self).get_description_context()
        d.update({
            'parent_model_verbose_name':
                six.text_type(self.parent_model._meta.verbose_name),
            'parent_model_verbose_name_plural':
                six.text_type(self.parent_model._meta.verbose_name_plural),
        })
        return d

    def get_parent_object(self):
        parent_filter = {
            self.lookup_field: self.kwargs.get(self.lookup_field, None),
        }
        return get_object_or_404(self.parent_model, **parent_filter)

    def check_parent_access(self, parent=None):
        parent = parent or self.get_parent_object()
        parent_access = getattr(self, 'parent_access', 'read')
        if parent_access in ('read', 'delete'):
            args = (parent_access, parent)
        else:
            args = (parent_access, parent, None)
        if not check_user_access(self.request.user, self.parent_model, *args):
            # logger.debug('check_parent_access: parent_access=%s parent=%s',
            # parent_access, parent.__class__.__name__)
            raise PermissionDenied()

    def get_queryset(self):
        parent = self.get_parent_object()
        self.check_parent_access(parent)
        qs = self.model.objects.all().distinct()
        sublist_qs = getattr(parent, self.relationship).distinct()
        return qs & sublist_qs


class RetrieveAPIView(generics.RetrieveAPIView, GenericAPIView):
    pass


class RetrieveUpdateAPIView(RetrieveAPIView, generics.RetrieveUpdateAPIView):

    def pre_save(self, obj):
        super(RetrieveUpdateAPIView, self).pre_save(obj)
        if hasattr(obj, 'owner'):
            obj.owner = self.request.user

    def update(self, request, *args, **kwargs):
        self.update_filter(request, *args, **kwargs)
        return super(RetrieveUpdateAPIView, self).update(
            request, *args, **kwargs)

    def update_filter(self, request, *args, **kwargs):
        """Scrub any fields the user cannot/should not put/patch,
        based on user context.

        This runs after read-only serialization filtering.
        """
        pass


class RetrieveUpdateDestroyAPIView(
        RetrieveUpdateAPIView,
        generics.RetrieveUpdateDestroyAPIView):
    pass
