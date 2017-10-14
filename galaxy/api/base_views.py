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
import inspect
import warnings
import logging

# Django
from django.http import Http404
from django.core.paginator import InvalidPage
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

# Django REST Framework
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import clone_request
from rest_framework import status
from rest_framework import views

# local
from galaxy.api.access import check_user_access
from galaxy.api.utils import get_object_or_400, camelcase_to_underscore
from galaxy.main.models import RoleRating

# FIXME: machinery for auto-adding audit trail logs to all CREATE/EDITS

__all__ = [
    'APIView', 'GenericAPIView', 'ListAPIView', 'ListCreateAPIView',
    'SubListAPIView', 'SubListCreateAPIView', 'RetrieveAPIView',
    'RetrieveUpdateAPIView', 'RetrieveUpdateDestroyAPIView',
]

logger = logging.getLogger('galaxy.api.base_views')


def get_view_name(cls, suffix=None):
    '''
    Wrapper around REST framework get_view_name() to support get_name() method
    and view_name property on a view class.
    '''
    name = ''
    if hasattr(cls, 'get_name') and callable(cls.get_name):
        name = cls().get_name()
    elif hasattr(cls, 'view_name'):
        if callable(cls.view_name):
            name = cls.view_name()
        else:
            name = cls.view_name
    if name:
        return ('%s %s' % (name, suffix)) if suffix else name
    return views.get_view_name(cls, suffix=None)


def get_view_description(cls, html=False):
    '''
    Wrapper around REST framework get_view_description() to support
    get_description() method and view_description property on a view class.
    '''
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
            if resp_hdr.split()[0] and resp_hdr.split()[0] == req_hdr.split()[0]:
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
    # Base class for all model-based views.

    # Subclasses should define:
    #   model = ModelClass
    #   serializer_class = SerializerClass

    def get_queryset(self):
        qs = self.model.objects.all().distinct()
        if hasattr(self.model, "is_active"):
            return qs.filter(is_active=True)
        else:
            return qs.filter(active=True)

    def get_description_context(self):
        # Set instance attributes needed to get serializer metadata.
        if not hasattr(self, 'request'):
            self.request = None
        if not hasattr(self, 'format_kwarg'):
            self.format_kwarg = 'format'
        d = super(GenericAPIView, self).get_description_context()
        d.update({
            'model_verbose_name': unicode(self.model._meta.verbose_name),
            'model_verbose_name_plural': unicode(self.model._meta.verbose_name_plural),
            'serializer_fields': self.get_serializer().metadata(),
        })
        return d

    def metadata(self, request):
        '''
        Add field information for GET requests (so field names/labels are
        available even when we can't POST/PUT).
        '''
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
            except:
                pass
            else:
                # If user has appropriate permissions for the view, include
                # appropriate metadata about the fields that should be supplied.
                serializer = self.get_serializer()
                actions['GET'] = serializer.metadata()
        if actions:
            ret['actions'] = actions
        if getattr(self, 'search_fields', None):
            ret['search_fields'] = self.search_fields
        return ret

    def paginate_queryset(self, queryset, page_size=None):
        """
        Paginate a queryset if required, either returning a page object,
        or `None` if pagination is not configured for this view.
        """
        deprecated_style = False
        if page_size is not None:
            warnings.warn('The `page_size` parameter to `paginate_queryset()` '
                          'is due to be deprecated. '
                          'Note that the return style of this method is also '
                          'changed, and will simply return a page object '
                          'when called without a `page_size` argument.',
                          PendingDeprecationWarning, stacklevel=2)
            deprecated_style = True
        else:
            # Determine the required page size.
            # If pagination is not configured, simply return None.
            page_size = self.get_paginate_by()
            if not page_size:
                return None
        # if not self.allow_empty:
        #      warnings.warn(
        #          'The `allow_empty` parameter is due to be deprecated. '
        #          'To use `allow_empty=False` style behavior, You should override '
        #          '`get_queryset()` and explicitly raise a 404 on empty querysets.',
        #          PendingDeprecationWarning, stacklevel=2
        #      )

        paginator = self.paginator_class(queryset, page_size,
                                         allow_empty_first_page=True)
        page_kwarg = self.kwargs.get(self.page_kwarg)
        page_query_param = self.request.QUERY_PARAMS.get(self.page_kwarg)
        page = page_kwarg or page_query_param or 1
        try:
            page_number = generics.strict_positive_int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404("Page is not 'last', nor can it be converted to an int.")
        try:
            page = paginator.page(page_number)
        except InvalidPage as e:
            # here is where we override the default paginator behavior
            # rather than fail, try and return a valid page
            try:
                if page_number > paginator.num_pages:
                    page = paginator.page(paginator.num_pages)
                else:
                    page = paginator.page(1)
            except:
                raise Http404('Invalid page (%(page_number)s): %(message)s' % {
                    'page_number': page_number,
                    'message': str(e)
                })

        if deprecated_style:
            return (paginator, page, page.object_list, page.has_other_pages())
        return page


class ListAPIView(generics.ListAPIView, GenericAPIView):
    # Base class for a read-only list view.

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


class ListCreateAPIView(ListAPIView, generics.ListCreateAPIView):
    # Base class for a list view that allows creating new objects.

    def pre_save(self, obj):
        if hasattr(self.model, 'owner'):
            obj['owner_id'] = self.request.user.id


class SubListAPIView(ListAPIView):
    # Base class for a read-only sublist view.

    # Subclasses should define at least:
    #   model = ModelClass
    #   serializer_class = SerializerClass
    #   parent_model = ModelClass
    #   relationship = 'rel_name_from_parent_to_model'
    # And optionally (user must have given access permission on parent object
    # to view sublist):
    #   parent_access = 'read'

    def get_description_context(self):
        d = super(SubListAPIView, self).get_description_context()
        d.update({
            'parent_model_verbose_name': unicode(self.parent_model._meta.verbose_name),
            'parent_model_verbose_name_plural': unicode(self.parent_model._meta.verbose_name_plural),
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
            # logger.debug('check_parent_access: parent_access=%s parent=%s', parent_access, parent.__class__.__name__)
            raise PermissionDenied()

    def get_queryset(self):
        parent = self.get_parent_object()
        self.check_parent_access(parent)
        qs = self.model.objects.all().distinct()
        sublist_qs = getattr(parent, self.relationship).distinct()
        return qs & sublist_qs


class SubListCreateAPIView(SubListAPIView, ListCreateAPIView):
    # Base class for a sublist view that allows for creating subobjects and
    # attaching/detaching them from the parent.

    # In addition to SubListAPIView properties, subclasses may define (if the
    # sub_obj requires a foreign key to the parent):
    #   parent_key = 'field_on_model_referring_to_parent'

    def get_description_context(self):
        d = super(SubListCreateAPIView, self).get_description_context()
        d.update({
            'parent_key': getattr(self, 'parent_key', None),
        })
        return d

    def create(self, request, *args, **kwargs):
        # If the object ID was not specified, it probably doesn't exist in the
        # DB yet. We want to see if we can create it.  The URL may choose to
        # inject it's primary key into the object because we are posting to a
        # subcollection. Use all the normal access control mechanisms.

        # Make a copy of the data provided (since it's readonly) in order to
        # inject additional data.

        if hasattr(request.DATA, 'dict'):
            data = request.DATA.dict()
        else:
            data = request.DATA

        # add the parent key to the post data using the pk from the URL
        parent_key = getattr(self, 'parent_key', None)
        # logger.debug('SubListCreateAPIView.create: parent_key=%s', parent_key)
        if parent_key:
            data[parent_key] = self.kwargs['pk']
        # logger.debug('SubListCreateAPIView.create: data.parent_key=%s', data[parent_key])

        # attempt to deserialize the object
        try:
            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                # logger.debug('SubListCreateAPIView.create: serializer failed validation')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception, e:
            # logger.debug('SubListCreateAPIView.create: serializer threw an error')
            return Response("serializer errors", status=status.HTTP_400_BAD_REQUEST)

        # Verify we have permission to add the object as given.
        if not check_user_access(request.user, self.model, 'add', serializer.validated_data):
            # logger.debug('SubListCreateAPIView.create: permission denied user=%s model=%s action=add',
            #             request.user, self.model._meta.verbose_name)
            raise PermissionDenied()

        # save the object through the serializer, reload and return the saved
        # object deserialized

        try:
            self.pre_save(serializer.validated_data)
            obj = serializer.save()
            data = self.serializer_class(obj).data
        except IntegrityError, e:
            return Response("database integrity conflict", status=status.HTTP_409_CONFLICT)
        except Exception, e:
            return Response("unknown error: %s" % str(e), status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def attach(self, request, *args, **kwargs):
        attached = False
        created = False
        modified = False
        parent = self.get_parent_object()
        relationship = getattr(parent, self.relationship)
        sub_id = request.DATA.get('id', None)
        data = request.DATA

        # FIXME: We have special case handling for RoleRatings
        #        which would probably be better moved into
        #        a new class and overridden completely
        is_role_rating = isinstance(parent, RoleRating)
        #logger.debug('SubListCreateAPIView.attach: parent=%s', parent.__class__.__name__)

        # Create the sub object if an ID is not provided.
        # We never create objects when attaching to a RoleRating
        if not sub_id and not is_role_rating:
            try:
                response = self.create(request, *args, **kwargs)
                if response.status_code != status.HTTP_201_CREATED:
                    return response
                sub_id = response.data['id']
                data = response.data
                try:
                    location = response['Location']
                except KeyError:
                    location = None
                created = True
            except:
                # logger.debug('SubListCreateAPIView.attach: not sub_id and not is_role_rating threw Permission Denied')
                raise PermissionDenied()

        # Retrive the sub object (whether created or by ID).
        sub = get_object_or_400(self.model, pk=sub_id)

        # likewise with creation, we never try and update
        # the sub-object if we're dealing with a RoleRating
        if not created and not is_role_rating:
            # Update the object to make sure the data is correct, but
            # verify we have permission to edit before trying to update
            if not check_user_access(request.user, self.model, 'change', sub, data):
                raise PermissionDenied()
            else:
                sub.__dict__.update(data)
                if sub.is_dirty:
                    sub.save()
                    modified = True

        # Verify we have permission to attach.
        if not check_user_access(request.user, self.parent_model,
                                 'attach', parent, sub,
                                 self.relationship, data,
                                 skip_sub_obj_read_check=created):
            raise PermissionDenied()

        # Attach the object to the collection.
        if sub not in relationship.all():
            relationship.add(sub)
            attached = True

        # SPECIAL CASE
        # FIXME: the base view for objects with mutually exclusive
        #        relationship should probably be split off into a
        #        new view, which codifies the mutually exclusive things
        #if attached and is_role_rating:
            """
            Up/down votes are mutually exclusive. If we've attached
            the user to one of the lists, we need to make sure we
            remove them from the other (if they're in it).
            """
            # mux_relationship = None
            # if self.relationship == 'up_votes':
            #    mux_relationship = getattr(parent, 'down_votes')
            # elif self.relationship == 'down_votes':
            #    mux_relationship = getattr(parent, 'up_votes')
            # if mux_relationship and sub in mux_relationship.all():
            #    mux_relationship.remove(sub)

        if created:
            headers = {}
            if location:
                headers['Location'] = location
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        elif modified or attached:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def unattach(self, request, *args, **kwargs):
        sub_id = request.DATA.get('id', None)
        if not sub_id:
            data = dict(msg='"id" is required to disassociate')
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        parent = self.get_parent_object()
        parent_key = getattr(self, 'parent_key', None)
        relationship = getattr(parent, self.relationship)
        sub = get_object_or_400(self.model, pk=sub_id)

        #if not request.user.can_access(self.parent_model, 'unattach', parent,
        if not check_user_access(request.user, self.parent_model, 'unattach',
                                 parent, sub, self.relationship):
            raise PermissionDenied()

        if parent_key:
            # sub object has a ForeignKey to the parent, so we can't remove it
            # from the set, only mark it as inactive.
            sub.mark_inactive()
        else:
            relationship.remove(sub)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        if not isinstance(request.DATA, dict):
            return Response('invalid type for post data',
                            status=status.HTTP_400_BAD_REQUEST)
        if 'disassociate' in request.DATA:
            return self.unattach(request, *args, **kwargs)
        else:
            return self.attach(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class RetrieveAPIView(generics.RetrieveAPIView, GenericAPIView):
    pass


class RetrieveUpdateAPIView(RetrieveAPIView, generics.RetrieveUpdateAPIView):

    def pre_save(self, obj):
        super(RetrieveUpdateAPIView, self).pre_save(obj)
        if hasattr(obj, 'owner'):
            obj.owner = self.request.user

    def update(self, request, *args, **kwargs):
        self.update_filter(request, *args, **kwargs)
        return super(RetrieveUpdateAPIView, self).update(request, *args, **kwargs)

    def update_filter(self, request, *args, **kwargs):
        ''' scrub any fields the user cannot/should not put/patch, based on user context.  This runs after read-only serialization filtering '''
        pass


class RetrieveUpdateDestroyAPIView(RetrieveUpdateAPIView, generics.RetrieveUpdateDestroyAPIView):
    pass
#     def destroy(self, request, *args, **kwargs):
#         # somewhat lame that delete has to call it's own permissions check
#         obj = self.get_object()
#         # FIXME: Why isn't the active check being caught earlier by RBAC?
#         if getattr(obj, 'active', True) == False:
#             raise Http404()
#         if getattr(obj, 'is_active', True) == False:
#             raise Http404()
#         if not check_user_access(request.user, self.model, 'delete', obj):
#             raise PermissionDenied()
#         if hasattr(obj, 'mark_inactive'):
#             obj.mark_inactive()
#         else:
#             raise NotImplementedError('destroy() not implemented yet for %s' % obj)
#         return HttpResponse(status=204)
