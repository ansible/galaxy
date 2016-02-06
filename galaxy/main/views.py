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

import datetime
import json
import hashlib
import random
import re
import smtplib
import string
import markdown
from hashlib import sha256 as sha
from math import ceil, floor

from django.conf import settings
from django.contrib.auth import login as authlogin
from django.contrib.auth import logout as authlogout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.cache import cache
from django.core.context_processors import csrf
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Count, Avg
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import timezone
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.detail import DetailView

# local stuff
import urls as main_urls

from galaxy.api.utils import html_decode
from models import *
from forms import *
from utils import db_common
from celerytasks.tasks import import_role

# rst2html5-tools
from html5css3 import Writer
from docutils.core import publish_string

User = get_user_model()
common_services = [
    'js/commonServices/tagService.js',
    'js/commonServices/meService.js',
    'js/commonServices/ratingService.js',
    'js/commonServices/roleService.js',
    'js/commonServices/roleSearchService.js',
    'js/commonServices/storageService.js',
    'js/commonServices/userService.js',
    'js/commonServices/platformService.js',
    'js/commonServices/galaxyUtilities.js',
    'js/commonServices/searchService.js',
    'js/commonDirectives/commonDirectives.js',
    'js/commonDirectives/autocompleteDirective.js',
    'js/commonDirectives/textCollapseDirective.js',
    'js/commonDirectives/dotDotDotDirective.js',
    'js/commonServices/relatedService.js',
    'js/commonServices/paginateService.js',
    'js/commonServices/githubRepoService.js',
    'js/commonServices/importService.js',
    'js/commonServices/githubClickService.js',
]

#------------------------------------------------------------------------------
# Helpers
#------------------------------------------------------------------------------
def readme_to_html(obj):
    # Expects obj to be an instance of Role

    if obj is None or obj.readme is None:
        return ''
    if obj.readme_type is None or obj.readme_type == 'md':
        return markdown.markdown(obj.readme, extensions=['extra'])
    if obj.readme_type == 'rst':
        settings = {'input_encoding': 'utf8'}
        return publish_string(
            source=obj.readme,
            writer=Writer(),
            writer_name='html5css3',
            settings_overrides=settings,
        ).decode('utf8')

def get_settings():
    settings = None
    try:
        settings = Settings.objects.all().order_by('-id')[0]
    except: pass
    return settings

def build_standard_context(request):
    context = {}

    context['version'] = settings.version
    
    # everything gets the request user and a csrf token,
    # just in case it might need them
    context["request"] = request
    context["user"] = request.user
    context["debug"] = 'on' if settings.DEBUG else 'off'
    context.update(csrf(request))

    # the default redirect url is the current path
    context["redirect_url"] = request.path

    # the following code generates a list of url chunks
    # plus the href to them, assuming the chunk matches
    # one of the patterns in the urls list. This is used
    # to create a breadcrumb widget on each page.
    url_parts = request.path.split('/')
    total_path = ""
    url_items = [["home","/"],]
    for part in url_parts:
        if part != "":
            total_path += "/%s" % part
            breadcrumb_url = None
            for up in main_urls.urlpatterns:
                if up.__class__.__name__ == 'RegexURLPattern':
                    try:
                        up.regex.match(total_path[1:]).groups()
                        breadcrumb_url = total_path
                        break
                    except: pass
            url_items.append([part,breadcrumb_url])
    context["url_items"] = url_items
    context["url_items_length"] = len(url_items)
    context["site_name"] = settings.SITE_NAME
    context["use_menu_controller"] = False
    context["load_angular"] = False

    if request.user.is_authenticated():
        context["connected_to_github"] = False
        for account in request.user.socialaccount_set.all():
            if account.provider == 'github':
                context["connected_to_github"] = True

    return context

#------------------------------------------------------------------------------
# Non-secure URLs
#------------------------------------------------------------------------------
# def home(request):
#     context = build_standard_context(request)
#     context["ng_app"] = "mainApp"
#     context["extra_js"] = [
#       'js/apps/main_app.js',
#       'js/controllers/main.js',
#       'js/commonServices/roles.js',
#       'js/commonServices/categories.js',
#       'js/commonServices/users.js',
#     ]
#     return render_to_response('home.html', context)

def home(request):
    context = build_standard_context(request)
    return render_to_response('home.html', context)

def explore(request):
    context = build_standard_context(request)
    context["ng_app"] = "exploreApp"
    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
          'js/exploreApp/exploreApp.js',
          'js/exploreApp/exploreController.js',
          'js/commonServices/roleSearchService.js',
          'js/commonServices/tagService.js',
          'js/commonServices/userService.js',
          'js/commonServices/galaxyUtilities.js',
          'js/commonDirectives/dotDotDotDirective.js',
        ]
    else:
        context["extra_js"] = [
          'dist/galaxy.exploreApp.min.js'
        ]
    context['load_angular'] = True
    context['page_title'] = 'Explore'
    return render_to_response('explore.html', context)

def intro(request):
    context = build_standard_context(request)
    context['page_title'] = 'About'
    return render_to_response('intro.html', context)

def accounts_landing(request):
    if request.user.is_authenticated():
        request.session["transient"] = {"status":"info","msg":"Redirected to your dashboard."}
        return HttpResponseRedirect("/accounts/profile/")
    else:
        context = build_standard_context(request)
        return render_to_response('account/landing.html', context)

def list_category(request, category=None, page=1):
    context = build_standard_context(request)
    context["ng_app"] = "listApp"
    context["extra_css"] = []
    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
          'js/listApp/listApp.js',
          'js/listApp/roleListController.js',
          'js/listApp/menuController.js',
        ] + common_services
    else:
        context["extra_js"] = [
          'dist/galaxy.listApp.min.js'
        ]
    context["use_menu_controller"] = True
    context["load_angular"] = True
    context["page_title"] = "Browse Roles"
    return render_to_response('list_category.html', context)

def detail_category(request, category=None, page=1):
    context = build_standard_context(request)
    context["ng_app"] = "detailApp"
    context["ng_controller"] = "HeaderCtrl"
    context["extra_css"] = []
    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
            # 'js/angular-slider.min.js',
            'js/detailApp/detailApp.js',
            'js/detailApp/roleDetailController.js',
            'js/detailApp/menuController.js',
            'js/detailApp/headerController.js',
            'js/detailApp/headerService.js',
        ] + common_services
    else:
        context["extra_js"] = [
            'dist/galaxy.detailApp.min.js'
        ]
    context["use_menu_controller"] = True
    context["load_angular"] = True
    context["page_title"] = "Role Details"
    return render_to_response('list_category.html', context)

def role_add_view(request, category=None, page=1):
    context = build_standard_context(request)
    context["ng_app"] = "roleAddApp"
    context["extra_css"] = []
    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
            'js/roleAddApp/roleAddApp.js',
            'js/roleAddApp/roleAddController.js',
            'js/detailApp/menuController.js',
            'js/roleAddApp/notificationSecretService.js',
        ] + common_services
    else:
        context["extra_js"] = [
            'dist/galaxy.roleAddApp.min.js'
        ]
    context["use_menu_controller"] = False
    context["load_angular"] = True
    context["page_title"] = "My Roles"
    app_id = ""
    if settings.SITE_NAME == 'galaxy.ansible.com':
        app_id = '3e92491593df34c92089'
    if settings.SITE_NAME == 'galaxy-qa.ansible.com':
        app_id = '2e6b1de3b2832a7cf974'
    if settings.SITE_NAME == 'localhost':
        app_id = '3232f7f9f6477dee707f'
    context["auth_orgs_url"] = "https://github.com/settings/connections/applications/%s" % app_id
    return render_to_response('list_category.html', context)

def handle_404_view(request):
    context = {}
    context["page_title"] = "404 Error"
    return render_to_response('custom404.html')

def handle_400_view(request):
    context = {}
    context["page_title"] = "400 Error"
    return render_to_response('custom400.html')

class NamespaceListView(ListView):
    model = 'Role'
    template_name = 'namespace_list.html'
    context_object_name = 'namespaces'
    paginate_by = 20

    def get_queryset(self):
        author = self.request.GET.get('author')
        if author:
            qs = Role.objects.filter(active=True,is_valid=True,namespace__icontains=author).order_by('namespace').distinct('namespace')
        else:
            qs = Role.objects.filter(active=True,is_valid=True).order_by('namespace').distinct('namespace')
        return qs

    def get_context_data(self, **kwargs):
        context = super(NamespaceListView, self).get_context_data(**kwargs)
        context['search_value'] = self.request.GET.get('author', '')
        context["site_name"] = settings.SITE_NAME
        context["load_angular"] = False       
        context["page_title"] = "Browse Authors"
        # the paginator includes 
        qs = self.get_queryset()
        context['count'] = qs.count()

        # figure out the range of pages numbers to show in bootstrap paging widget
        page_obj = context['page_obj']
        paginator = context['paginator']
        if page_obj.number % 10 == 0:
            first = int(floor((page_obj.number - 1)/10.0) * 10 + 1)
        else:
            first = int(floor(page_obj.number/10.0) * 10 + 1)
        first = 1 if first <= 0 else first
        last = int(ceil(page_obj.number/10.0) * 10)
        last = paginator.num_pages if last > paginator.num_pages else last
        context['page_range'] = range(first, last + 1)
        return context

class RoleListView(ListView):
    template_name = 'role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        self.namespace = self.args[0]
        name = self.request.GET.get('role', None)
        if Role.objects.filter(namespace=self.args[0]).count() == 0:
            raise Http404()
        if name:
            qs = Role.objectsfilter(active=True,is_valid=True,namespace=self.args[0],name__icontains=name)
        else:
            qs = Role.objects.filter(active=True,is_valid=True,namespace=self.args[0])
        return qs

    def get_context_data(self, **kwargs):
        context = super(RoleListView, self).get_context_data(**kwargs)
        try:
            ns = Namespace.objects.get(namespace=self.namespace)
            context['namespace'] = dict(
                avatar_url=ns.avatar_url,
                location=ns.location,
                company=ns.company,
                name=ns.name,
                email=ns.email,
                html_url=ns.html_url,
                followers=ns.followers,
                description=ns.description
            )
        except:
            context['namespace'] = None
        context['namespace_name'] = self.namespace
        context['search_value'] = self.request.GET.get('role', '')
        context["site_name"] = settings.SITE_NAME
        context["load_angular"] = False
        context["page_title"] = self.namespace
        context["meta_description"] = "Roles contributed by %s." % self.namespace
        return context

class RoleDetailView(DetailView):
    template_name = 'role_detail.html'
    context_obj_name = 'role'

    def get_object(self):
        self.namespace = self.args[0]
        self.name = self.args[1]
        self.role = get_object_or_404(Role, namespace=self.namespace, name=self.name, active=True, is_valid=True)
        return self.role

    def get_context_data(self, **kwargs):
        context = super(RoleDetailView, self).get_context_data(**kwargs)

        try:
            ns = Namespace.objects.get(namespace=self.namespace)
            context['namespace'] = dict(
                avatar_url=ns.avatar_url,
                location=ns.location,
                company=ns.company,
                name=ns.name,
                email=ns.email,
                html_url=ns.html_url,
                followers=ns.followers,
                description=ns.description
            )
        except:
            context['namespace'] = None

        context['namespace_name'] = self.namespace
        context['name'] = self.name 
        context["site_name"] = settings.SITE_NAME
        context["load_angular"] = False
        context["meta_description"] = "Role %s.%s - %s" % (self.role.namespace, self.role.name, self.role.description)
        
        try:
            gh_user = User.objects.get(github_user=self.role.github_user)
            context['avatar'] = gh_user.github_avatar
        except:
            context['avatar'] = "img/avatar.png";

        user = self.request.user
        context['is_authenticated'] = True if user.is_authenticated() and user.is_connected_to_github() else False
        context['is_staff'] = user.is_staff

        context['is_subscriber'] = False
        if user.is_authenticated():
            sub = user.get_subscriber(self.role.github_user, self.role.github_repo)
            if sub:
                context['is_subscriber'] = True 
                context['subscriber_id'] = sub.id
        
        context['is_stargazer'] = False
        if user.is_authenticated():
             star = user.get_stargazer(self.role.github_user, self.role.github_repo)
             if star:
                context['is_stargazer'] = True
                context['stargazer_id'] = star.id
        
        role = self.role
        context['tags'] = role.tags.all()
        context['platforms'] = role.platforms.all()
        context['dependencies'] = role.dependencies.all()
        
        context['versions'] = []
        for ver in role.versions.all():
            context['versions'].append({
                'loose_version': ver.loose_version,
                'release_date':  ver.release_date.strftime('%m/%d/%Y %H:%M:%I %p') if ver.release_date else 'NA'
            })

        context['create_date'] = role.created.strftime('%m/%d/%Y %H:%M:%I %p')
        context['import_date'] = role.imported.strftime('%m/%d/%Y %H:%M:%I %p') if role.imported else 'NA'
        context['readme_html'] = readme_to_html(role)
        context['page_title'] = "%s.%s" % (self.namespace, self.name)
        return context


#------------------------------------------------------------------------------
# Non-secured Action URLs requiring a POST
#------------------------------------------------------------------------------

@require_POST
def prefs_set_sort(request):
    redirect_url = request.REQUEST.get("redirect_url",None)
    if not redirect_url:
        request.session["transient"] = {"status":"danger","msg":"An invalid action was requested."}
        return HttpResponseRedirect("/")
    sort_category = request.REQUEST.get("sort_category",None)
    sort_order = request.REQUEST.get("sort_order",None)
    if sort_category and sort_order:
        request.session["sort_%s" % sort_category] = sort_order
    return HttpResponseRedirect(redirect_url)

#------------------------------------------------------------------------------
# Logged in/secured URLs
#------------------------------------------------------------------------------

@login_required
def import_status_view(request):
    """
    Allow logged in users to view the status of import requests.
    """
    context = build_standard_context(request)
    context["ng_app"] = "importStatusApp"
    context["extra_css"] = []

    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
            'js/importStatusApp/importStatusApp.js',
            'js/importStatusApp/importStatusController.js',
            'js/commonServices/galaxyUtilities.js',
        ] + common_services
    else:
        context["extra_js"] = [
            'dist/galaxy.importStatusApp.min.js'
        ]

    if request.session.has_key("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]
    
    context["load_angular"] = True
    context["page_title"] = "My Imports"
    return render_to_response('import_status.html',context)


@login_required
def accounts_profile(request):
    """
    This is the logged in user's landing page, which
    will display all of their current licenses plus any
    invoices that have yet to be paid.
    """
    context = build_standard_context(request)
    context["ng_app"] = "accountsApp"
    context["extra_css"] = [
    ]
    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
          'js/commonServices/meService.js',
          'js/commonServices/storageService.js',
          'js/commonServices/relatedService.js',
          'js/commonServices/galaxyUtilities.js',
          'js/accountApp/myRolesController.js',
          'js/accountApp/accountApp.js',
        ]
    else:
        context["extra_js"] = [
          'dist/galaxy.accountApp.min.js'
        ]

    if request.session.has_key("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    return render_to_response('account/profile.html',context)

@login_required
def accounts_connect(request):
    context = build_standard_context(request)
    return render_to_response('socialaccount/connections.html',context)

@login_required
def accounts_connect_success(request):
    context = build_standard_context(request)
    context["connected_to_github"] = True
    return render_to_response('socialaccount/connections.html',context)

@login_required
@transaction.non_atomic_requests
def accounts_role_refresh(request, id=None):
    try:
        role = Role(pk=id)
    except Exception, e:
        request.session["transient"] = {"status":"info","msg":"Failed: %s" % e}
    else:
        # check to see if there's already a running task for this
        # role. if so, don't start another one.
        try:
            role_import = role.imports.latest()
            if role_import.state in ("", "RUNNING"):
                request.session["transient"] = {"status":"info","msg":"An import task for this role has already been started."}
                return HttpResponseRedirect(reverse('main:accounts-profile'))
        except Exception, e:
            #transaction.rollback()
            #request.session["transient"] = {"status":"danger","msg":"An error occurred looking up the task info for this role: %s." % e}
            #return HttpResponseRedirect(reverse('main:accounts-profile'))
            pass
        with transaction.atomic():
            # start the celery task to run the import and save
            # its info back to the database for later reference
            task = import_role.delay(role.id)
            role_import = RoleImport()
            role_import.name = "%s-%s" % (role.name, task.id)
            role_import.celery_task_id = task.id
            role_import.role = role
            role_import.save()
        request.session["transient"] = {"status":"info","msg":"Role refresh scheduled successfully."}
    # redirect back home no matter what
    return HttpResponseRedirect(reverse('main:accounts-profile'))

@login_required
@transaction.non_atomic_requests
def accounts_role_delete(request, id=None):
    try:
        with transaction.atomic():
            role = Role.objects.get(pk=id, owner__id=request.user.id)
            if role.is_valid and role.active:
                request.session["transient"] = {"status":"danger","msg":"That role is still active, you must deactivate it before deleting it."}
            else:
                role.delete()
                request.session["transient"] = {"status":"info","msg":"The role was deleted successfully."}
    except:
        request.session["transient"] = {"status":"danger","msg":"An error was encountered while deleting the role you requested."}
    # redirect back home
    return HttpResponseRedirect(reverse('main:accounts-profile'))

@login_required
@transaction.non_atomic_requests
def accounts_role_deactivate(request, id=None):
    try:
        with transaction.atomic():
            role = Role.objects.get(pk=id, owner__id=request.user.id)
            if role.is_valid and role.active:
                role.mark_inactive()
                request.session["transient"] = {"status":"info","msg":"The role was deleted successfully."}
    except:
        request.session["transient"] = {"status":"danger","msg":"An error was encountered while deleting the role you requested."}
    # redirect back home
    return HttpResponseRedirect(reverse('main:accounts-profile'))

@login_required
@transaction.non_atomic_requests
def accounts_role_reactivate(request, id=None):
    try:
        with transaction.atomic():
            role = Role.objects.get(pk=id, owner__id=request.user.id)
            if role.is_valid and not role.active:
                role.mark_active()
            request.session["transient"] = {"status":"info","msg":"The role was re-activated successfully."}
    except:
        request.session["transient"] = {"status":"danger","msg":"An error was encountered while re-activating the role you requested."}
    # redirect back home
    return HttpResponseRedirect(reverse('main:accounts-profile'))


@login_required
def accounts_role_view(request, role=None):
    try:
        role_obj = Role.objects.get(name=role, owner=request.user)
    except:
        request.session["transient"] = {"status":"info","msg":"No valid role was found with that name."}
        return HttpResponseRedirect(reverse('main:accounts-profile'))

    context = build_standard_context(request)
    context["role"] = role_obj
    return render_to_response('account/role_view.html', context)
