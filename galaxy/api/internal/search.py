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
import functools
import operator

from django.contrib.postgres import search as psql_search
from django.db.models import fields as db_fields
from django.db.models.expressions import Func, F, Case, When, Value, \
    ExpressionWrapper as Expr, RawSQL
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q

from galaxy import constants
from galaxy.main import models


__all__ = (
    'CollectionSearch',
    'ContentSearch',
)


RANK_FUNCTION = 'ts_rank'
RANK_NORMALIZATION = 32

VENDOR_RANK = 0.1
DOWNLOAD_RANK_MULTIPLIER = 0.4
CONTENT_SCORE_MULTIPLIER = 0.2
COMMUNITY_SCORE_MODIFIER = 0.002
COMMUNITY_SCORE_MODIFIER_MIN = 0.005

CONTENT_MATCH_QUERY = """
    SELECT json_agg(json_build_object('name', cvc ->> 'name',
                                      'content_type', cvc ->> 'content_type'))
    FROM jsonb_array_elements("main_collectionversion"."contents") AS cvc
    WHERE plainto_tsquery(%s) @@ to_tsvector(cvc ->> 'name')
"""


class BaseSearch:
    def __init__(self, filters, order_by='relevance', order='desc'):
        self.filters = filters
        self.order_by = order_by
        self.order = order

    def count(self):
        raise NotImplementedError

    def search(self):
        raise NotImplementedError


class CollectionSearch(BaseSearch):
    """Builds queries to search for collections."""

    def count(self):
        """Returns number of matching collections."""
        return self._base_queryset().count()

    def search(self):
        qs = self._base_queryset().select_related('latest_version')
        qs = self._add_relevance(qs)
        qs = self._add_order_by(qs)
        return qs

    def _base_queryset(self):
        """Returns generic queryset used both for count and search."""
        qs = models.Collection.objects.order_by()

        keywords = self.filters.get('keywords')
        if keywords:
            qs = qs.filter(
                search_vector=psql_search.SearchQuery(keywords))

        ns_type = self.filters.get('contributor_type')
        if ns_type:
            qs = qs.filter(namespace__is_vendor=(
                ns_type == constants.NS_TYPE_PARTNER))

        namespaces = self.filters.get('namespaces')
        if namespaces:
            filters = [Q(namespace__name__icontains=name)
                       for name in self.filters['namespaces']]
            qs = qs.filter(functools.reduce(operator.or_, filters))

        names = self.filters.get('names')
        if names:
            filters = [Q(name__icontains=name) for name in names]
            qs = qs.filter(functools.reduce(operator.or_, filters))

        tags = self.filters.get('tags')
        if tags:
            tags_qs = models.Tag.objects.filter(name__in=tags)
            qs = qs.distinct().filter(tags__in=tags_qs)

        deprecated = self.filters.get('deprecated')
        if deprecated:
            qs = qs.filter(deprecated=deprecated)

        return qs

    def _add_relevance(self, qs):
        if self.filters.get('keywords'):
            return self._add_keyword_relevance(qs)
        else:
            return self._add_quality_relevance(qs)

    def _add_keyword_relevance(self, qs):
        """Annotates query with search rank value.

        Search rank is calculated as result of `ts_rank` PostgreSQL
        function, which ranks vectors based on the frequency of their matching
        lexemes. Search rank is normalized by dividing it by itself + 1:
        """
        ts_rank_fn = Func(
            F('search_vector'),
            psql_search.SearchQuery(self.filters['keywords']),
            RANK_NORMALIZATION,
            function=RANK_FUNCTION,
            output_field=db_fields.FloatField()
        )
        return qs.annotate(relevance=ts_rank_fn)

    def _add_quality_relevance(self, qs):
        """Annotates query with relevance based on quality score.

        It is calculated by a formula:
            R = log(Q + 1) + 0.1 * v
        Where:
            R - Relevance;
            Q - Quality score (0 to 5);
            v - 1 if collection belongs to a partner namespace, otherwise 0.
        """
        quality_rank_expr = (
            Func(Coalesce(F('latest_version__quality_score'), 0) + 1,
                 function='log')
            * CONTENT_SCORE_MULTIPLIER
        )
        vendor_rank_expr = Case(
            When(namespace__is_vendor=True, then=Value(VENDOR_RANK)),
            When(namespace__is_vendor=False, then=Value(0)),
        )
        relevance_expr = F('quality_rank') + F('vendor_rank')
        return qs.annotate(
            quality_rank=Expr(
                quality_rank_expr, output_field=db_fields.FloatField()),
            vendor_rank=Expr(
                vendor_rank_expr, output_field=db_fields.FloatField()),
            relevance=Expr(
                relevance_expr, output_field=db_fields.FloatField()),
        )

    def _add_order_by(self, qs):
        order_by = self.order_by
        prefix = '-' if self.order == 'desc' else ''
        if order_by == 'qualname':
            order_by = [prefix + 'namespace__name', prefix + 'name']
        else:
            order_by = [prefix + order_by]
        return qs.order_by(*order_by)

    def _add_content_match(self, collections):
        keywords = self.filters.get('keywords')
        if not keywords:
            return

        ids = [c.latest_version_id for c in collections]
        content_match_query = RawSQL(CONTENT_MATCH_QUERY, params=(keywords,))
        versions = (
            models.CollectionVersion.objects.all()
            .annotate(content_match=content_match_query)
            .values('pk', 'content_match')
            .filter(pk__in=ids)
        )
        content_match = {v['pk']: v['content_match'] for v in versions}
        for collection in collections:
            collection.content_match = content_match.get(
                collection.latest_version_id)


class ContentSearch(BaseSearch):
    """Builds queries to search for content."""

    def count(self):
        """Returns number of matching content items."""
        return self._base_queryset().count()

    def search(self):
        qs = self._base_queryset().select_related(
            'content_type',
            'namespace',
            'repository',
            'repository__provider_namespace',
            'repository__provider_namespace__namespace',
        ).prefetch_related(
            'videos',
            'tags',
            'dependencies',
            'platforms',
            'repository__versions',
        )
        qs = self._add_search_rank(qs)
        qs = self._add_relevance(qs)
        qs = self._add_order_by(qs)
        return qs

    def _base_queryset(self):
        """Returns generic queryset used both for count and search."""
        qs = models.Content.objects.order_by().filter(
            repository__provider_namespace__namespace__isnull=False,
            repository__provider_namespace__namespace__active=True
        )

        keywords = self.filters.get('keywords')
        if keywords:
            qs = qs.filter(search_vector=psql_search.SearchQuery(keywords))

        ns_type = self.filters.get('contributor_type')
        if ns_type:
            qs = qs.filter(namespace__is_vendor=(
                ns_type == constants.NS_TYPE_PARTNER))

        namespaces = self.filters.get('namespaces')
        if namespaces:
            filters = [Q(namespace__name__icontains=name)
                       for name in self.filters['namespaces']]
            qs = qs.filter(functools.reduce(operator.or_, filters))

        names = self.filters.get('names')
        if names:
            filters = [Q(name__icontains=name) for name in names]
            qs = qs.filter(functools.reduce(operator.or_, filters))

        tags = self.filters.get('tags')
        if tags:
            tags_qs = models.Tag.objects.filter(name__in=tags)
            qs = qs.distinct().filter(tags__in=tags_qs)

        deprecated = self.filters.get('deprecated')
        if deprecated:
            qs = qs.filter(repository__deprecated=deprecated)

        platforms = self.filters.get('platforms')
        if platforms:
            platforms_qs = models.Platform.objects.filter(
                name__in=platforms)
            qs = qs.distinct().filter(platforms__in=platforms_qs)

        clouds = self.filters.get('cloud_platforms')
        if clouds:
            clouds_qs = models.CloudPlatform.objects.filter(
                name__in=clouds)
            qs = qs.distinct().filter(cloud_platforms__in=clouds_qs)

        return qs

    def _add_search_rank(self, qs):
        """Annotates query with search rank value.

        Search rank is calculated as result of `ts_rank` PostgreSQL
        function, which ranks vectors based on the frequency of their matching
        lexemes. Search rank is normalized by dividing it by itself + 1:
        """
        keywords = self.filters.get('keywords')
        if not keywords:
            return qs.annotate(
                search_rank=Value(0.0, output_field=db_fields.FloatField()))
        search_rank_fn = Func(
            F('search_vector'),
            psql_search.SearchQuery(keywords),
            RANK_NORMALIZATION,
            function=RANK_FUNCTION,
            output_field=db_fields.FloatField())
        return qs.annotate(search_rank=search_rank_fn)

    def _add_relevance(self, qs):
        """Annotates query with relevance rank and its constituent values.

        Relevance is calculated by a formula:

            R = Sr + Dr + Qr,

        where
            R - relevance;
            Sr - search rank (from 0 to 1);
            Dr - download rank;
            Qr - quality rank;

                   ts_rank()
            Sr = -------------
                 ts_rank() + 1

        For more details on search rank see `_add_search_rank` function.

        Download rank is calculated by a formula:

                         ln(cd + 1)
            Dr = 0.4 * --------------
                       ln(cd + 1) + 1

        Quality rank is calculated by a formula:

            Qr = 0.2 * log(Q + 1)

        """
        c = 'repository__community_score'
        d = 'repository__download_count'

        # ln((MOD*c + MIN) * d + 1)
        # where c = community_score and d = download_count
        # We're using the community_score as a modifier to the download count
        # instead of just allocating a certain number of points based on the
        # score. The reason for this is that the download score is
        # a logaritmic scale so adding a fixed number of points ended up
        # boosting scores way too much for content with low numbers of
        # downloads. This system allows for the weight of the community score
        # to scale with the number of downloads
        download_count_ln_expr = Func(
            (((Coalesce(F(c), 0) * COMMUNITY_SCORE_MODIFIER) +
              COMMUNITY_SCORE_MODIFIER_MIN)
             * F(d)) + 1,
            function='ln'
        )
        download_rank_expr = (
                F('download_count_ln')
                / (1 + F('download_count_ln'))
                * DOWNLOAD_RANK_MULTIPLIER
        )

        q = 'repository__quality_score'
        # This function is better than using a linear function because it
        # makes it so that the effect of losing the first few points is
        # relatively minor, which reduces the impact of errors in scoring.
        quality_rank_expr = (
                Func(Coalesce(F(q), 0) + 1, function='log')
                * CONTENT_SCORE_MULTIPLIER
        )

        relevance_expr = (
                F('search_rank') + F('download_rank') + F('quality_rank')
        )

        return qs.annotate(
            download_count_ln=Expr(
                download_count_ln_expr,
                output_field=db_fields.FloatField()),
            download_rank=Expr(
                download_rank_expr,
                output_field=db_fields.FloatField()),
            quality_rank=Expr(
                quality_rank_expr,
                output_field=db_fields.FloatField()),
            relevance=Expr(
                relevance_expr,
                output_field=db_fields.FloatField()),
        )

    def _add_order_by(self, qs):
        order_by = self.order_by
        prefix = '-' if self.order == 'desc' else ''
        if order_by == 'qualname':
            order_by = [prefix + 'namespace__name', prefix + 'name']
        elif order_by == 'download_count':
            order_by = [prefix + 'repository__download_count']
        else:
            order_by = [prefix + order_by]
        return qs.order_by(*order_by)
