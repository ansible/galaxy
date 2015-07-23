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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import timezone
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt                                                        
from django.views.decorators.http import require_POST

# local stuff
import urls as main_urls

from models import *
from forms import *
from utils import db_common
from celerytasks.tasks import import_role

User = get_user_model()

#------------------------------------------------------------------------------
# Helpers
#------------------------------------------------------------------------------

def get_settings():
    settings = None
    try:
        settings = Settings.objects.all().order_by('-id')[0]
    except: pass
    return settings

def build_standard_context(request):
    context = {}

    # everything gets the request user and a csrf token,
    # just in case it might need them
    context["user"] = request.user
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
    context["site_name"] = settings.SITE_NAME
    # database operations for data that is available on every page
    # categories
    categories = Category.objects.all()
    context["categories"] = categories
    # number of roles per category
    context["roles_per_category"] = Category.objects.values('name').annotate(num_roles=Count('roles')).order_by('-num_roles','name')[0:10]
    # top X roles
    context["top_roles"] = Role.objects.all().order_by('-bayesian_score')[0:10]
    # top X users
    #context["top_users"] = User.objects.all().order_by('-average_score')[0:10]
    # top X reviewers
    context["top_reviewers"] = User.objects.all().order_by('-karma')[0:10]
    # last X new roles
    context["new_roles"] = Role.objects.all().order_by('-date_added')[0:10]
    # last X new users
    context["new_users"] = User.objects.all().order_by('-date_joined')[0:10]
    # and we're done
    return context

#------------------------------------------------------------------------------
# Non-secure URLs
#------------------------------------------------------------------------------
# def home(request):
#     context = build_standard_context(request)
#     context["ng_app"] = "mainApp"
#     context["extra_js"] = [
#       '/static/js/apps/main_app.js',
#       '/static/js/controllers/main.js',
#       '/static/js/services/roles.js',
#       '/static/js/services/categories.js',
#       '/static/js/services/users.js',
#     ]
#     return render_to_response('home.html', context)

def home(request):
    context = build_standard_context(request)
    return render_to_response('home.html', context)

def styles(request):
    context = build_standard_context(request)
    return render_to_response('styles.html', context)

def explore(request):
    context = build_standard_context(request)
    context["ng_app"] = "mainApp"
    context["extra_js"] = [
      '/static/js/main.js'
    ]
    return render_to_response('explore.html', context)

def intro(request):
    context = build_standard_context(request)
    context["page_title"] = "About"
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
    context["ng_app"] = "roleApp"
    context["extra_css"] = [
    ]
    context["extra_js"] = [
        '/static/js/list.js'
    ]
    return render_to_response('list_category.html', context)

def role_view(request, user, role):
    role = Role.objects.get(name=role, owner__username=user)
    awx_avg_scores = role.ratings.filter(voter__is_staff=True).values('role__name').annotate(
        ease_of_use      = Avg('ease_of_use'),
        documentation    = Avg('documentation'),
        best_practices   = Avg('best_practices'),
        repeatability    = Avg('repeatability'),
        platform_support = Avg('platform_support'),
        overall          = Avg('overall'),
        avg_score        = Avg('score'),
    )
    other_avg_scores = role.ratings.values('role__name').annotate(
        ease_of_use      = Avg('ease_of_use'),
        documentation    = Avg('documentation'),
        best_practices   = Avg('best_practices'),
        repeatability    = Avg('repeatability'),
        platform_support = Avg('platform_support'),
        overall          = Avg('overall'),
        avg_score        = Avg('score'),
    )
    awx_ratings = role.ratings.filter(voter__is_staff=True).order_by('-score')
    other_ratings = role.ratings.filter(voter__is_staff=False).order_by('-score')

    context = build_standard_context(request)
    context["role"]             = role
    context["awx_ratings"]      = awx_ratings
    context["other_ratings"]    = other_ratings
    if len(awx_avg_scores) > 0:
        context["awx_avg_scores"] = awx_avg_scores[0]
    if len(other_avg_scores) > 0:
        context["other_avg_scores"] = other_avg_scores[0]

    return render_to_response('role_view.html', context)

def role_search(request):
    return HttpResponse("in role_search()")

def user_view(request, user):
    this_user = User.objects.get(username=user)
    all_avg_score = this_user.roles.values('owner').annotate(avg_score=Avg('ratings__score'))
    awx_avg_score = this_user.roles.filter(ratings__voter__is_staff=True).values('owner').annotate(avg_score=Avg('ratings__score'))

    context = build_standard_context(request)
    context["this_user"] = this_user
    context["user_roles"] = this_user.roles.all() #.order_by('-toprole__bayesian_score')
    if len(all_avg_score) > 0:
        context["all_avg_score"] = all_avg_score[0]
    if len(awx_avg_score) > 0:
        context["awx_avg_score"] = awx_avg_score[0]
    return render_to_response('user_view.html', context)

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
    context["extra_js"] = [
        '/static/js/accounts.js'
    ]

    if request.session.has_key("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    return render_to_response('account/profile.html',context)

@login_required
@transaction.non_atomic_requests
def accounts_role_save(request):
    regex = re.compile(r'^(ansible[-_.+]*)*(role[-_.+]*)*')
    if request.method == 'POST':
        try:
            with transaction.atomic():
                form = RoleForm(request.POST)
                if form.is_valid():
                    # create the role, committing manually so that 
                    # we ensure the database is updated before we
                    # kick off the celery task to do the import
                    cd = form.cleaned_data
                    role = Role()
                    role.owner             = request.user
                    role.github_user       = cd['github_user']
                    role.github_repo       = cd['github_repo']
                    role.name              = cd.get('name',None) or cd['github_repo']
                    role.is_valid          = False

                    # strip out unwanted sub-strings from the name
                    role.name = regex.sub('', role.name)

                    role.save()
                    # commit the data to the database upon exiting the
                    # transaction.atomic() block, to make sure it's available
                    # for the celery task when it runs
                else:
                    context = build_standard_context(request)
                    context["form"] = form
                    return render_to_response('account/role_add.html', context)
        except IntegrityError, e:
            request.session["transient"] = {"status":"info","msg":"You have already created a role with that name."}
        except Exception, e:
            request.session["transient"] = {"status":"info","msg":"Failed: %s" % e}
        else:
            with transaction.atomic():
                # start the celery task to run the import and save
                # its info back to the database for later reference
                task = import_role.delay(role.id)
                role_import = RoleImport()
                role_import.celery_task_id = task.id
                role_import.role = role
                role_import.save()
            request.session["transient"] = {"status":"info","msg":"Role created successfully, import task started."}
    else:
        request.session["transient"] = {"status":"info","msg":"Invalid method."}
    # redirect back home no matter what
    return HttpResponseRedirect(reverse('main:accounts-profile'))

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
def accounts_role_add(request):
    form = RoleForm()
    context = build_standard_context(request)
    context["form"] = form
    return render_to_response('account/role_add.html', context)

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

