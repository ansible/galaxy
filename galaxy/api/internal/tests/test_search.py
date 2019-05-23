# (c) 2012-2019, Ansible by Red Hat
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

import typing as t

from django.test import TestCase

from galaxy import constants
from galaxy.main import models
from galaxy.api.internal.search import (
    BaseSearch, CollectionSearch, ContentSearch
)


class CommonSearchTestMixin:
    def _create_content(self, namespace: str, name: str, **kwargs):
        raise NotImplementedError

    def _create_namespace(
            self, name: str, is_vendor: bool = False) -> models.Namespace:
        obj = models.Namespace.objects.create(name=name, is_vendor=is_vendor)
        self.namespaces[name] = obj
        return obj

    def _assert_search_results(
            self, query: BaseSearch, expected: t.List[str],
            check_order: bool = False) -> t.NoReturn:
        assert query.count() == len(expected)
        result_names = [item.name for item in query.search()]
        match_names = [self.content[name].name for name in expected]

        if check_order:
            assert result_names == match_names
        else:
            assert sorted(result_names) == sorted(match_names)

    def _init_data(self) -> t.NoReturn:
        self.namespaces = {}
        self.content = {}

        self._create_namespace('webtools')
        self._create_namespace('cloudtools', is_vendor=True)

        self._create_content(
            namespace='webtools', name='nginx', version='1.0.0',
            description='Nginx is a web server which can also be used '
                        'as a reverse proxy, load balancer, mail proxy '
                        'and HTTP cache.',
            download_count=830000,
            quality_score=4.9,
            tags=['web', 'nginx', 'reverse', 'proxy'],
            cloud_platforms=['gcloud'],
            contents=[
                {'content_type': 'role', 'name': 'nginx'},
            ],
        )
        self._create_content(
            namespace='webtools', name='apache2', version='1.0.0',
            description='The Apache HTTP Server, colloquially called Apache, '
                        'is free and open-source cross-platform web '
                        'server software.',
            download_count=6000,
            quality_score=3.0,
            deprecated=True,
            tags=['apache', 'web', 'webserver', 'httpd'],
            contents=[
                {'content_type': 'role', 'name': 'httpd'},
            ],
        )
        self._create_content(
            namespace='webtools', name='uwsgi', version='1.0.0',
            description='uWSGI is a software application that "aims at '
                        'developing a full stack for building hosting '
                        'services".',
            download_count=490000,
            quality_score=4.5,
            tags=['development', 'web', 'wsgi'],
            contents=[
                {'content_type': 'role', 'name': 'uwsgi'},
                {'content_type': 'role', 'name': 'uwsgi-docker'},
            ],
        )

        self._create_content(
            namespace='cloudtools', name='openstack', version='1.0.0',
            description='OpenStack is a free and open-source software '
                        'platform for cloud computing',
            download_count=850000,
            quality_score=4.5,
            tags=['cloud', 'openstack'],
            platforms=['debian:stretch', 'ubuntu:xenial'],
            cloud_platforms=['aws'],
            contents=[
                {'content_type': 'role', 'name': 'nova'},
                {'content_type': 'role', 'name': 'neutron'},
                {'content_type': 'role', 'name': 'cinder'},
            ],
        )
        self._create_content(
            namespace='cloudtools', name='docker', version='1.0.0',
            description='Docker is a collection of interoperating '
                        'software-as-a-service and platform-as-a-service '
                        'offerings.',
            download_count=150000,
            quality_score=4.2,
            tags=['cloud', 'docker', 'containers'],
            platforms=['debian:stretch', 'ubuntu:xenial'],
            contents=[
                {'content_type': 'role', 'name': 'docker'},
            ],
        )
        self._create_content(
            namespace='cloudtools', name='kubernetes', version='1.0.0',
            description='Kubernetes is an open-source container-orchestration '
                        'system for automating application deployment, '
                        'scaling, and management.',
            download_count=770000,
            quality_score=4.7,
            tags=['cloud', 'kubernetes', 'k8s', 'containers'],
            platforms=['centos:6', 'centos:7', 'ubuntu:xenial'],
            cloud_platforms=['aws', 'gcloud'],
            contents=[
                {'content_type': 'module', 'name': 'k8s_service'},
                {'content_type': 'module', 'name': 'k8s_deploymentconfig'},
                {'content_type': 'module', 'name': 'k8s_route'},
            ],
        )


class TestCollectionSearch(CommonSearchTestMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._init_data()

    def _create_content(
            self,
            namespace: str,
            name: str,
            **kwargs,
    ) -> models.Collection:
        namespace_obj = self.namespaces[namespace]
        collection_obj = models.Collection.objects.create(
            namespace=namespace_obj,
            name=name,
            deprecated=kwargs.get('deprecated', False),
            download_count=kwargs.get('download_count', 0)
        )
        for tag in kwargs.get('tags', []):
            tag_obj, _ = models.Tag.objects.get_or_create(name=tag)
            collection_obj.tags.add(tag_obj)
        self.content[name] = collection_obj

        version_obj = models.CollectionVersion.objects.create(
            collection=collection_obj,
            version=kwargs.get('version', '1.0.0'),
            metadata={
                'namespace': namespace,
                'name': name,
                'description': kwargs.get('description', ''),
                'tags': kwargs.get('tags', [])
            },
            contents=kwargs.get('contents', []),
            quality_score=kwargs.get('quality_score', 0.)
        )
        collection_obj.latest_version = version_obj
        collection_obj.save()
        return collection_obj

    def test_filter_by_keyword_in_name(self):
        query = CollectionSearch({'keywords': 'openstack'})
        self._assert_search_results(query, ['openstack'])

    def test_filter_by_keyword_in_namespace(self):
        query = CollectionSearch({'keywords': 'cloudtools'})
        self._assert_search_results(
            query, ['docker', 'openstack', 'kubernetes'])

    def test_filter_by_keyword_in_description(self):
        query = CollectionSearch({'keywords': 'balancer'})
        self._assert_search_results(query, ['nginx'])

    def test_filter_by_keyword_in_tags(self):
        query = CollectionSearch({'keywords': 'httpd'})
        self._assert_search_results(query, ['apache2'])

    def test_filter_by_keyword_in_modules(self):
        query = CollectionSearch({'keywords': 'cinder'})
        self._assert_search_results(query, ['openstack'])

    def test_filter_by_one_namespace(self):
        # Search by full namespace
        query = CollectionSearch({'namespaces': ['webtools']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

        # Search by partial namespace
        query = CollectionSearch({'namespaces': ['web']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_many_namespaces(self):
        # Search by full namespace
        query = CollectionSearch({'namespaces': ['cloudtools', 'webtools']})
        expected = ['openstack', 'docker', 'kubernetes',
                    'nginx', 'apache2', 'uwsgi']
        self._assert_search_results(query, expected)

        # Search by partial namespaces
        query = CollectionSearch({'namespaces': ['cloud', 'web']})
        expected = ['openstack', 'docker', 'kubernetes',
                    'nginx', 'apache2', 'uwsgi']
        self._assert_search_results(query, expected)

        # Search by parts of the same namespace
        query = CollectionSearch({'namespaces': ['webto', 'btools']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_one_name(self):
        # Search by full name
        query = CollectionSearch({'names': ['apache2']})
        self._assert_search_results(query, ['apache2'])

        # Search by partial name
        query = CollectionSearch({'names': ['apac']})
        self._assert_search_results(query, ['apache2'])

    def test_filter_by_many_names(self):
        # Search by full names
        query = CollectionSearch({'names': ['apache2', 'nginx']})
        self._assert_search_results(query, ['apache2', 'nginx'])

        # Search by partial names
        query = CollectionSearch({'names': ['apac', 'ngi']})
        self._assert_search_results(query, ['apache2', 'nginx'])

    def test_filter_by_ns_type(self):
        query = CollectionSearch({'contributor_type': 'partner'})
        self._assert_search_results(
            query, ['docker', 'openstack', 'kubernetes'])

        query = CollectionSearch({'contributor_type': 'community'})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_tags(self):
        query = CollectionSearch({'tags': ['proxy']})
        self._assert_search_results(query, ['nginx'])

        query = CollectionSearch({'tags': ['web']})
        self._assert_search_results(query, ['apache2', 'nginx', 'uwsgi'])

        query = CollectionSearch({'tags': ['web', 'nginx']})
        self._assert_search_results(query, ['apache2', 'nginx', 'uwsgi'])

    def test_filter_by_deprecated(self):
        query = CollectionSearch({'deprecated': True})
        self._assert_search_results(query, ['apache2'])

    def test_filter_by_many_params(self):
        query = CollectionSearch({'keywords': 'free', 'tags': ['cloud']})
        self._assert_search_results(query, ['openstack'])

    def test_order_by_keyword_relevance(self):
        query = CollectionSearch({'keywords': 'docker'})
        self._assert_search_results(
            query, ['docker', 'uwsgi'], check_order=True)

        query = CollectionSearch({'keywords': 'docker'}, order='asc')
        self._assert_search_results(
            query, ['uwsgi', 'docker'], check_order=True)

    def test_order_by_quality_relevance(self):
        # TODO(cutwater): Requires discussion of quality relevance function.
        pass

    def test_order_by_download_count(self):
        expected = ['openstack', 'nginx', 'kubernetes',
                    'uwsgi', 'docker', 'apache2']
        query = CollectionSearch({}, order_by='download_count', order='desc')
        self._assert_search_results(query, expected, check_order=True)

        query = CollectionSearch({}, order_by='download_count', order='asc')
        self._assert_search_results(
            query, list(reversed(expected)), check_order=True)

    def test_order_by_name(self):
        expected = ['apache2', 'docker', 'kubernetes',
                    'nginx', 'openstack', 'uwsgi']
        query = CollectionSearch({}, order_by='name', order='asc')
        self._assert_search_results(query, expected, check_order=True)

        query = CollectionSearch({}, order_by='name', order='desc')
        self._assert_search_results(
            query, list(reversed(expected)), check_order=True)

    def test_order_by_qualname(self):
        expected = ['docker', 'kubernetes', 'openstack',
                    'apache2',  'nginx', 'uwsgi']
        query = CollectionSearch({}, order_by='qualname', order='asc')
        self._assert_search_results(query, expected, check_order=True)

        expected = ['uwsgi', 'nginx', 'apache2',
                    'openstack', 'kubernetes', 'docker']
        query = CollectionSearch({}, order_by='qualname', order='desc')
        self._assert_search_results(query, expected, check_order=True)


class TestContentSearch(CommonSearchTestMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._init_data()

    def _create_content(
            self,
            namespace: str,
            name: str,
            **kwargs,
    ) -> models.Content:
        ns = self.namespaces[namespace]
        provider = models.Provider.objects.get(name='GitHub')
        content_type = models.ContentType.get(constants.ContentType.ROLE)
        provider_ns = models.ProviderNamespace.objects.create(
            provider=provider, namespace=ns, name=name)
        repository = models.Repository.objects.create(
            name=name, provider_namespace=provider_ns,
            deprecated=kwargs.get('deprecated', False),
            download_count=kwargs.get('download_count', 0),
        )
        content = models.Content.objects.create(
            namespace=ns,
            name=name,
            repository=repository,
            content_type=content_type,
            description=kwargs.get('description', ''),
            quality_score=kwargs.get('quality_score', 0.)

        )
        self.content[name] = content

        for tag_name in kwargs.get('tags', []):
            tag, _ = models.Tag.objects.get_or_create(name=tag_name)
            content.tags.add(tag)

        for platform_name in kwargs.get('platforms', []):
            name, release = platform_name.split(':')
            platform, _ = models.Platform.objects.get_or_create(
                name=name, release=release)
            content.platforms.add(platform)

        for cloud_name in kwargs.get('cloud_platforms', []):
            cloud, _ = models.CloudPlatform.objects.get_or_create(
                name=cloud_name)
            content.cloud_platforms.add(cloud)

        return content

    def test_filter_by_keyword_in_name(self):
        query = ContentSearch({'keywords': 'openstack'})
        self._assert_search_results(query, ['openstack'])

    def test_filter_by_keyword_in_namespace(self):
        query = ContentSearch({'keywords': 'cloudtools'})
        self._assert_search_results(
            query, ['docker', 'openstack', 'kubernetes'])

    def test_filter_by_keyword_in_description(self):
        query = ContentSearch({'keywords': 'balancer'})
        self._assert_search_results(query, ['nginx'])

    def test_filter_by_one_namespace(self):
        # Search by full namespace
        query = ContentSearch({'namespaces': ['webtools']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

        # Search by partial namespace
        query = ContentSearch({'namespaces': ['web']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_many_namespaces(self):
        # Search by full namespace
        query = ContentSearch({'namespaces': ['cloudtools', 'webtools']})
        expected = ['openstack', 'docker', 'kubernetes',
                    'nginx', 'apache2', 'uwsgi']
        self._assert_search_results(query, expected)

        # Search by partial namespaces
        query = ContentSearch({'namespaces': ['cloud', 'web']})
        expected = ['openstack', 'docker', 'kubernetes',
                    'nginx', 'apache2', 'uwsgi']
        self._assert_search_results(query, expected)

        # Search by parts of the same namespace
        query = ContentSearch({'namespaces': ['webto', 'btools']})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_one_name(self):
        # Search by full name
        query = ContentSearch({'names': ['apache2']})
        self._assert_search_results(query, ['apache2'])

        # Search by partial name
        query = ContentSearch({'names': ['apac']})
        self._assert_search_results(query, ['apache2'])

    def test_filter_by_many_names(self):
        # Search by full names
        query = ContentSearch({'names': ['apache2', 'nginx']})
        self._assert_search_results(query, ['apache2', 'nginx'])

        # Search by partial names
        query = ContentSearch({'names': ['apac', 'ngi']})
        self._assert_search_results(query, ['apache2', 'nginx'])

    def test_filter_by_ns_type(self):
        query = ContentSearch({'contributor_type': 'partner'})
        self._assert_search_results(
            query, ['docker', 'openstack', 'kubernetes'])

        query = ContentSearch({'contributor_type': 'community'})
        self._assert_search_results(
            query, ['nginx', 'apache2', 'uwsgi'])

    def test_filter_by_tags(self):
        query = ContentSearch({'tags': ['proxy']})
        self._assert_search_results(query, ['nginx'])

    def test_filter_by_deprecated(self):
        query = ContentSearch({'deprecated': True})
        self._assert_search_results(query, ['apache2'])

    def test_filter_by_many_params(self):
        query = ContentSearch({'keywords': 'free', 'tags': ['cloud']})
        self._assert_search_results(query, ['openstack'])

    def test_filter_by_platform(self):
        query = ContentSearch({'platforms': ['debian']})
        self._assert_search_results(query, ['docker', 'openstack'])

        query = ContentSearch({'platforms': ['debian', 'ubuntu', 'centos']})
        self._assert_search_results(
            query, ['docker', 'openstack', 'kubernetes'])

    def test_filter_by_cloud_platform(self):
        query = ContentSearch({'cloud_platforms': ['aws']})
        self._assert_search_results(query, ['kubernetes', 'openstack'])

        query = ContentSearch({'cloud_platforms': ['gcloud']})
        self._assert_search_results(query, ['kubernetes', 'nginx'])

        query = ContentSearch({'cloud_platforms': ['aws', 'gcloud']})
        print(query.search())
        self._assert_search_results(
            query, ['kubernetes', 'openstack', 'nginx'])

    def test_order_by_relevance(self):
        query = ContentSearch(
            {'keywords': 'server'}, order_by='relevance', order='desc')
        self._assert_search_results(
            query, ['nginx', 'apache2'], check_order=True)

        query = ContentSearch(
            {'keywords': 'server'}, order_by='relevance', order='asc')
        self._assert_search_results(
            query, ['apache2', 'nginx'], check_order=True)

    def test_order_by_download_count(self):
        expected = ['openstack', 'nginx', 'kubernetes',
                    'uwsgi', 'docker', 'apache2']
        query = ContentSearch({}, order_by='download_count', order='desc')
        self._assert_search_results(query, expected, check_order=True)

        query = ContentSearch({}, order_by='download_count', order='asc')
        self._assert_search_results(
            query, list(reversed(expected)), check_order=True)

    def test_order_by_name(self):
        expected = ['apache2', 'docker', 'kubernetes',
                    'nginx', 'openstack', 'uwsgi']
        query = ContentSearch({}, order_by='name', order='asc')
        self._assert_search_results(query, expected, check_order=True)

        query = ContentSearch({}, order_by='name', order='desc')
        self._assert_search_results(
            query, list(reversed(expected)), check_order=True)

    def test_order_by_qualname(self):
        expected = ['docker', 'kubernetes', 'openstack',
                    'apache2',  'nginx', 'uwsgi']
        query = ContentSearch({}, order_by='qualname', order='asc')
        self._assert_search_results(query, expected, check_order=True)

        expected = ['uwsgi', 'nginx', 'apache2',
                    'openstack', 'kubernetes', 'docker']
        query = ContentSearch({}, order_by='qualname', order='desc')
        self._assert_search_results(query, expected, check_order=True)
