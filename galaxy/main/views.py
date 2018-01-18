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

import markdown

from math import ceil, floor

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView

# local stuff
from galaxy.main.models import Content, ProviderNamespace, ContentBlock

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
    'js/commonServices/userStarredService.js',
    'js/commonDirectives/commonDirectives.js',
    'js/commonDirectives/autocompleteDirective.js',
    'js/commonDirectives/textCollapseDirective.js',
    'js/commonDirectives/dotDotDotDirective.js',
    'js/commonServices/relatedService.js',
    'js/commonServices/paginateService.js',
    'js/commonServices/githubRepoService.js',
    'js/commonServices/importService.js',
    'js/commonServices/githubClickService.js',
    'js/commonServices/namespaceService.js',
    'js/commonServices/providerSourceService.js',
]

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------


def readme_to_html(obj):
    if obj is None:
        return ''
    if obj.readme_html:
        return obj.readme_html
    if not obj.readme:
        return ''
    content = ''
    if obj.readme_type is None or obj.readme_type == 'md':
        try:
            content = markdown.markdown(obj.readme, extensions=['extra'])
        except:
            content = "Failed to convert README to HTML. Galaxy now stores the GitHub generated HTML for your " \
                      "README. If you re-import this role, the HTML will show up, and this message will go away."

    if obj.readme_type == 'rst':
        settings = {'input_encoding': 'utf8'}
        try:
            content = publish_string(
                source=obj.readme,
                writer=Writer(),
                writer_name='html5css3',
                settings_overrides=settings,
            ).decode('utf8')
        except:
            content = "Failed to convert README to HTML. Galaxy now stores the GitHub generated HTML for your " \
                      "README. If you re-import this role, the HTML will show up, and this message will go away."

    return content


def get_url_parts(path):
    import urls as main_urls
    # create URLs for breadcrumbs displayed in page headers
    url_parts = path.split('/')
    total_path = ""
    url_items = [["home", "/"]]
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
                    except:
                        pass
            url_items.append([part, breadcrumb_url])
    return url_items


def build_standard_context(request):
    url_items = get_url_parts(request.path)
    debug = 'on' if settings.DEBUG else 'off'
    context = dict(
        request=request,
        user=request.user,
        debug=debug,
        redirect_url=request.path,
        url_items=url_items,
        url_items_length=len(url_items),
        site_name=settings.SITE_NAME,
        use_menu_controller=False,
        load_angular=False,
        connected_to_github=False
    )

    if request.user.is_authenticated():
        for account in request.user.socialaccount_set.all():
            if account.provider == 'github':
                context["connected_to_github"] = True

    return context

# ------------------------------------------------------------------------------
# Non-secure URLs
# ------------------------------------------------------------------------------


def home(request):
    context = build_standard_context(request)
    contentblocks = ContentBlock.objects.filter(name__in=[
        'main-title',
        'main-share',
        'main-downloads',
        'main-featured-blog'
    ]).all()
    context['contentblocks'] = {item.name: item for item in contentblocks}
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
        request.session["transient"] = {"status": "info", "msg": "Redirected to your dashboard."}
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
    context["page_title"] = "Content Details"
    return render_to_response('list_category.html', context)


def handle_404_view(request):
    context = dict(page_title="404 Error")
    return render_to_response('custom404.html', context, status=404)


def handle_400_view(request):
    context = dict(page_title="400 Error")
    return render_to_response('custom400.html', context, status=400)


def handle_500_view(request):
    context = dict(page_title="500 Error")
    return render_to_response('custom500.html', context, status=500)


class NamespaceListView(ListView):
    model = 'Content'
    template_name = 'namespace_list.html'
    context_object_name = 'namespaces'
    paginate_by = 20

    def get_queryset(self):
        author = self.request.GET.get('author')
        if author:
            qs = Content.objects.filter(active=True, is_valid=True, namespace__icontains=author).order_by('namespace').distinct('namespace')
        else:
            qs = Content.objects.filter(active=True, is_valid=True).order_by('namespace').distinct('namespace')
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

        # figure out the range of page numbers to show in paging widget
        page_obj = context['page_obj']
        paginator = context['paginator']
        if page_obj.number % 10 == 0:
            first = int(floor((page_obj.number - 1) / 10.0) * 10 + 1)
        else:
            first = int(floor(page_obj.number / 10.0) * 10 + 1)
        first = 1 if first <= 0 else first
        last = int(ceil(page_obj.number / 10.0) * 10)
        last = paginator.num_pages if last > paginator.num_pages else last
        context['page_range'] = range(first, last + 1)
        return context


class RoleListView(ListView):
    template_name = 'role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        self.namespace = self.args[0]
        name = self.request.GET.get('role', None)
        if Content.objects.filter(namespace=self.args[0]).count() == 0:
            raise Http404()
        if name:
            qs = Content.objects.filter(active=True, is_valid=True, namespace=self.args[0],
                                        name__icontains=name)
        else:
            qs = Content.objects.filter(active=True, is_valid=True, namespace=self.args[0])
        return qs

    def get_context_data(self, **kwargs):
        context = super(RoleListView, self).get_context_data(**kwargs)

        ns = None
        context['namespace'] = None
        if ProviderNamespace.objects.filter(namespace=self.namespace).count() > 0:
            ns = ProviderNamespace.objects.get(namespace=self.namespace)
        else:
            try:
                roles = list(self.get_queryset())
                ns = ProviderNamespace.objects.get(namespace=roles[0].github_user)
            except:
                pass

        if ns is not None:
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

        context['namespace_name'] = self.namespace
        context['search_value'] = self.request.GET.get('role', '')
        context["site_name"] = settings.SITE_NAME
        context["load_angular"] = False
        context["page_title"] = self.namespace
        context["meta_description"] = "Roles contributed by %s." % self.namespace
        return context


class RoleDetailView(DetailView):
    template_name = 'role_detail.html'
    model = Content
    context_object_name = 'role'

    def get_object(self, queryset=None):
        self.namespace = self.args[0]
        self.name = self.args[1]
        self.role = get_object_or_404(Content, namespace=self.namespace,
                                      name=self.name, active=True,
                                      is_valid=True)
        return self.role

    def get_context_data(self, **kwargs):
        context = super(RoleDetailView, self).get_context_data(**kwargs)

        try:
            ns = ProviderNamespace.objects.get(namespace=self.namespace)
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
        context["meta_description"] = "Content %s.%s - %s" % (self.role.namespace, self.role.name, self.role.description)

        try:
            gh_user = User.objects.get(github_user=self.role.github_user)
            context['avatar'] = gh_user.github_avatar
        except:
            context['avatar'] = "img/avatar.png"

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
        context['cloud_platforms'] = role.cloud_platforms.all()
        context['dependencies'] = role.dependencies.all()
        context['videos'] = role.videos.all()

        context['imports'] = []
        for imp_task in (role.repository.import_tasks
                         .all().order_by('-id')[:10]):
            context['imports'].append({
                'finished': imp_task.finished,
                'state': imp_task.state
            })

        for type in Content.ROLE_TYPE_CHOICES:
            if type[0] == role.role_type:
                context['role_type'] = type[1]
        if role.role_type == Content.ANSIBLE:
            context['install_command'] = 'ansible-galaxy install'
        elif role.role_type == Content.CONTAINER:
            context['install_command'] = 'ansible-container install'
        elif role.role_type == Content.CONTAINER_APP:
            context['install_command'] = 'ansible-container init'
        context['versions'] = []
        for ver in role.versions.all().order_by('-release_date'):
            context['versions'].append({
                'loose_version': ver.loose_version,
                'release_date': ver.release_date
            })
        context['import_date'] = role.imported
        context['last_commit_date'] = role.commit_created
        context['readme_html'] = readme_to_html(role)
        context['page_title'] = "%s.%s" % (self.namespace, self.name)
        return context


# ------------------------------------------------------------------------------
# Logged in/secured URLs
# ------------------------------------------------------------------------------


@login_required
def accounts_connect(request):
    context = build_standard_context(request)
    return render_to_response('socialaccount/connections.html', context)


@login_required
def accounts_connect_success(request):
    context = build_standard_context(request)
    context["connected_to_github"] = True
    return render_to_response('socialaccount/connections.html', context)


@login_required
def role_add_view(request):
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
    context["page_title"] = "My Content"

    app_id = ""
    if settings.SITE_NAME == 'galaxy.ansible.com':
        app_id = '3e92491593df34c92089'
    if settings.SITE_NAME == 'galaxy-qa.ansible.com':
        app_id = '2e6b1de3b2832a7cf974'
    if settings.SITE_NAME == 'localhost':
        app_id = '3232f7f9f6477dee707f'

    context["auth_orgs_url"] = "https://github.com/settings/connections/applications/%s" % app_id

    return render_to_response('list_category.html', context)


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

    if request.session.get("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    context["load_angular"] = True
    context["page_title"] = "My Imports"
    return render_to_response('import_status.html', context)


@login_required
def stars_list_view(request):
    context = build_standard_context(request)
    context["ng_app"] = "userStarredApp"
    context["extra_css"] = []

    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
            'js/userStarredApp/userStarredApp.js',
            'js/userStarredApp/userStarredController.js',
            'js/commonServices/galaxyUtilities.js',
        ] + common_services
    else:
        context["extra_js"] = [
            'dist/galaxy.userStarredApp.min.js'
        ]

    if request.session.get("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    context["load_angular"] = True
    context["page_title"] = "My Stars"
    return render_to_response('ng_view.html', context)


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

    if request.session.get("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    return render_to_response('account/profile.html', context)


@login_required
def my_namespaces_view(request):
    context = build_standard_context(request)
    context["ng_app"] = "namespaceApp"
    context["extra_css"] = []

    if settings.SITE_ENV == 'DEV':
        context["extra_js"] = [
            'js/namespaceApp/namespaceApp.js',
            'js/namespaceApp/namespaceController.js',
            'js/namespaceApp/namespaceAddController.js',
            'js/namespaceApp/namespaceEditController.js',
            'js/namespaceApp/namespaceFormService.js',
            'js/namespaceApp/menuController.js',
        ] + common_services
    else:
        context["extra_js"] = [
            'dist/galaxy.userStarredApp.min.js'
        ]

    if request.session.get("transient"):
        context["transient"] = request.session["transient"]
        del request.session["transient"]

    context["load_angular"] = True
    context["page_title"] = "My Namespaces"
    return render_to_response('ng_view.html', context)
