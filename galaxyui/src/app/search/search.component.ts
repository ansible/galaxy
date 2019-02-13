import { AfterViewInit, Component, OnInit } from '@angular/core';

import { ActivatedRoute } from '@angular/router';

import { Location } from '@angular/common';

import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';
import { ToolbarConfig } from 'patternfly-ng/toolbar/toolbar-config';

import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterEvent } from 'patternfly-ng/filter/filter-event';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterQuery } from 'patternfly-ng/filter/filter-query';
import { FilterType } from 'patternfly-ng/filter/filter-type';

import { SortConfig } from 'patternfly-ng/sort/sort-config';
import { SortEvent } from 'patternfly-ng/sort/sort-event';
import { SortField } from 'patternfly-ng/sort/sort-field';

import { EmptyStateConfig } from 'patternfly-ng/empty-state/empty-state-config';
import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { NotificationType } from 'patternfly-ng/notification/notification-type';

import { ContentTypes } from '../enums/content-types.enum';
import { CloudPlatform } from '../resources/cloud-platforms/cloud-platform';
import { ContentSearchService } from '../resources/content-search/content-search.service';
import { ContentType } from '../resources/content-types/content-type';
import { EventLoggerService } from '../resources/logger/event-logger.service';
import { PFBodyService } from '../resources/pf-body/pf-body.service';
import { Platform } from '../resources/platforms/platform';

import { ContentTypesIconClasses } from '../enums/content-types.enum';

import { RepoFormats } from '../enums/repo-types.enum';

import {
    ContributorTypes,
    ContributorTypesIconClasses,
} from '../enums/contributor-types.enum';

import { PopularEvent } from './popular/popular.component';

import { Content } from '../resources/content-search/content';

import { DefaultParams } from './search.resolver.service';

import * as moment from 'moment';
import { PluginTypes } from '../enums/plugin-types.enum';

@Component({
    selector: 'app-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.less'],
})
export class SearchComponent implements OnInit, AfterViewInit {
    // Used to track which component is being loaded
    componentName = 'SearchComponent';

    pageTitle = 'Search';
    pageIcon = 'fa fa-search';
    toolbarConfig: ToolbarConfig;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
    contentItems: Content[];
    listConfig: ListConfig;
    paginationConfig: PaginationConfig;

    emptyStateConfig: EmptyStateConfig;
    defaultEmptyStateTitle: string;
    noResultsState = 'No matching results found';

    pageLoading = true;
    showRelevance = true;
    showFilter = false;

    queryParams = { keywords: '' };
    sortAscending = false;
    pageSize = 10;
    pageNumber = 1;
    keywords = '';
    contentCount: number;

    appliedFilters: Filter[] = [];

    constructor(
        private route: ActivatedRoute,
        private contentSearch: ContentSearchService,
        private location: Location,
        private notificationService: NotificationService,
        private pfBody: PFBodyService,
        private eventLogger: EventLoggerService,
    ) {}

    ngOnInit() {
        this.pfBody.scrollToTop();
        this.filterConfig = {
            fields: [
                {
                    id: 'cloud_platforms',
                    title: 'Cloud Platform',
                    placeholder: 'Cloud Platform',
                    type: FilterType.TYPEAHEAD,
                    queries: [],
                },
                {
                    id: 'namespaces',
                    title: 'Contributor',
                    placeholder: 'Name',
                    type: FilterType.TEXT,
                },
                {
                    id: 'contributor_type',
                    title: 'Contributor Type',
                    placeholder: 'Contributor Type',
                    type: FilterType.TYPEAHEAD,
                    queries: [
                        {
                            id: ContributorTypes.community,
                            value: ContributorTypes.community,
                            iconStyleClass:
                                ContributorTypesIconClasses.community,
                        },
                        {
                            id: ContributorTypes.vendor,
                            value: ContributorTypes.vendor,
                            iconStyleClass: ContributorTypesIconClasses.vendor,
                        },
                    ],
                },
                {
                    id: 'deprecated',
                    title: 'Deprecated',
                    type: FilterType.TYPEAHEAD,
                    queries: [
                        {
                            id: 'true',
                            value: 'True',
                        },
                        {
                            id: 'false',
                            value: 'False',
                        },
                    ],
                },
                {
                    id: 'content_type',
                    title: 'Content Type',
                    placeholder: 'Content Type',
                    type: FilterType.TYPEAHEAD,
                    queries: [],
                },
                {
                    id: 'platforms',
                    title: 'Platform',
                    placeholder: 'Platform',
                    type: FilterType.TYPEAHEAD,
                    queries: [],
                },
                {
                    id: 'tags',
                    title: 'Tag',
                    placeholder: 'Tag',
                    type: FilterType.TEXT,
                },
            ] as FilterField[],
            resultsCount: 0,
            totalCount: 0,
            appliedFilters: [],
        } as FilterConfig;

        this.sortConfig = {
            fields: [] as SortField[],
            isAscending: true,
        } as SortConfig;

        this.emptyStateConfig = {
            info: '',
            title: this.noResultsState,
            iconStyleClass: 'pficon pficon-filter',
        } as EmptyStateConfig;

        this.toolbarConfig = {
            filterConfig: this.filterConfig,
            sortConfig: this.sortConfig,
        } as ToolbarConfig;

        this.listConfig = {
            emptyStateConfig: this.emptyStateConfig,
        } as ListConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0,
        } as PaginationConfig;

        this.route.queryParams.subscribe(params => {
            this.route.data.subscribe(data => {
                // This function is called each time the route updates, so
                // the default values have to be reset
                this.paginationConfig.pageNumber = 1;
                this.pageNumber = 1;

                this.preparePlatforms(data.platforms);
                this.prepareContentTypes(data.contentTypes);
                this.prepareCloudPlatforms(data.cloudPlatforms);

                // If there is an error on the search API, the content search services
                // returns nothing, so we have to check if results actually exist.
                if (data.content.results) {
                    // If no params exist, set to the default params
                    if (Object.keys(params).length === 0) {
                        params = DefaultParams.params;
                    }

                    // queryParams represents the complete query that will be made to the database
                    // and as such it essentially represents the state of the search page. When
                    // the page loads it is initialized from the URL params and used to set the
                    // state of each UI component. When those UI elements are set by the user,
                    // it needs to be updated to reflect the user's actions.
                    this.queryParams = JSON.parse(JSON.stringify(params));
                    if (this.queryParams['keywords'] === undefined) {
                        this.queryParams['keywords'] = '';
                    }

                    this.setSortConfig(this.queryParams);
                    this.setPageSize(this.queryParams);
                    this.setAppliedFilters(this.queryParams);
                    this.prepareContent(
                        data.content.results,
                        data.content.count,
                    );
                    this.setUrlParams(this.queryParams);
                    this.pageLoading = false;
                } else {
                    this.notificationService.message(
                        NotificationType.WARNING,
                        'Error',
                        'Invalid search query',
                        false,
                        null,
                        null,
                    );

                    this.setSortConfig(this.queryParams);
                    this.setPageSize(this.queryParams);
                    this.setAppliedFilters(this.queryParams);

                    this.pageLoading = false;
                }
            });
        });
    }

    ngAfterViewInit() {}

    toggleFilter() {
        this.showFilter = !this.showFilter;
    }

    sortChanged($event: SortEvent): void {
        let sortParams = '';
        if (!$event.isAscending) {
            sortParams += '-';
        }
        sortParams += $event.field.id;
        this.queryParams['order_by'] = sortParams;
        this.searchEntered();
    }

    filterChanged($event: FilterEvent): void {
        // Remove filters from queryParams
        for (const filter of this.filterConfig.fields) {
            if (this.queryParams[filter.id] !== undefined) {
                delete this.queryParams[filter.id];
            }
        }

        const filterby = {};
        const params = {};
        this.pageNumber = 1;
        this.paginationConfig.pageNumber = 1;
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach(filter => {
                if (filterby[filter.field.id] === undefined) {
                    filterby[filter.field.id] = [];
                }
                if (filter.field.type === FilterType.TYPEAHEAD) {
                    filterby[filter.field.id].push(filter.query.id);
                } else {
                    filterby[filter.field.id].push(filter.value);
                }
            });
            for (const key in filterby) {
                if (filterby.hasOwnProperty(key)) {
                    if (key === 'contributor_type') {
                        if (filterby[key].length === 1) {
                            switch (filterby[key][0]) {
                                case ContributorTypes.community:
                                    params['vendor'] = false;
                                    break;
                                case ContributorTypes.vendor:
                                    params['vendor'] = true;
                                    break;
                            }
                        }
                    } else {
                        params[key] = encodeURIComponent(
                            filterby[key].join(' '),
                        );
                    }
                }
            }
            this.appliedFilters = JSON.parse(
                JSON.stringify($event.appliedFilters),
            );

            // Apply new filters to queryParams
            for (const key of Object.keys(params)) {
                this.queryParams[key] = params[key];
            }
        } else {
            this.appliedFilters = [];
            this.contentItems = [];
        }
        this.searchEntered();
    }

    getToolbarConfig(): ToolbarConfig {
        this.toolbarConfig.filterConfig.appliedFilters = JSON.parse(
            JSON.stringify(this.appliedFilters),
        );
        return this.toolbarConfig;
    }

    handlePageChange($event: PaginationEvent) {
        let changed = false;
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            changed = true;
        } else if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            if (this.pageSize === this.paginationConfig.pageSize) {
                // changed pageNumber without changing pageSize
                this.pfBody.scrollToTop();
                changed = true;
            }
        }
        if (changed && !this.pageLoading) {
            this.queryParams['page_size'] = this.pageSize;
            this.queryParams['page'] = this.pageNumber;
            this.searchContent();
        }
    }

    handleWidgetClick($event: PopularEvent) {
        let update = false;
        if (this.queryParams[$event.itemType] === undefined) {
            this.queryParams[$event.itemType] = $event.item['name'];
            update = true;
        } else {
            if (
                !this.queryParams[$event.itemType].includes($event.item['name'])
            ) {
                update = true;
                this.queryParams[$event.itemType] += ' ' + $event.item['name'];
            }
        }

        if (update) {
            this.setAppliedFilters(this.queryParams);
            this.searchEntered();
        }
    }

    searchEntered() {
        this.queryParams['page'] = 1;
        this.pageNumber = 1;
        this.paginationConfig.pageNumber = 1;
        this.searchContent();
    }

    searchContent() {
        this.pageLoading = true;
        this.setUrlParams(this.queryParams);
        this.contentSearch.query(this.queryParams).subscribe(result => {
            this.prepareContent(result.results, result.count);
            this.pageLoading = false;
        });
    }

    contentClick(item: Content, index: number) {
        const itemNumber = (this.pageNumber - 1) * this.pageSize + index + 1;
        this.eventLogger.logSearchClick(
            this.queryParams,
            item.namespace_name + '.' + item.name,
            itemNumber,
            item.download_rank,
            item.search_rank,
            item.relevance,
            item.id,
        );
    }

    // private

    private setPageSize(params: any) {
        if (params['page_size']) {
            let pageSize = Number(params['page_size']);

            if (Number.isNaN(pageSize)) {
                pageSize = 10;
            }

            this.paginationConfig.pageSize = pageSize;
            this.pageSize = pageSize;
        }
        if (params['page']) {
            let pageNumber = Number(params['page']);

            if (Number.isNaN(pageNumber)) {
                pageNumber = 1;
            }

            this.paginationConfig.pageNumber = pageNumber;
            this.pageNumber = pageNumber;
        }
    }

    private setAppliedFilters(queryParams: any) {
        // Convert query params to filters
        this.appliedFilters = [];

        const params = JSON.parse(JSON.stringify(queryParams));

        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                if (key === 'vendor') {
                    const field = this.getFilterField('contributor_type');

                    const ffield: Filter = {} as Filter;
                    ffield.field = field;
                    field.queries.forEach((query: FilterQuery) => {
                        if (
                            query.id === ContributorTypes.community &&
                            params[key] === 'false'
                        ) {
                            ffield.query = query;
                            ffield.value = query.value;
                        } else if (
                            query.id === ContributorTypes.vendor &&
                            params[key] === 'true'
                        ) {
                            ffield.query = query;
                            ffield.value = query.value;
                        }
                    });
                    this.filterConfig.appliedFilters.push(ffield);
                    this.appliedFilters.push(ffield);
                } else {
                    const field = this.getFilterField(key);
                    if (!field) {
                        continue;
                    }

                    const values: string[] = params[key].split(' ');
                    values.forEach(v => {
                        const ffield: Filter = {} as Filter;
                        ffield.field = field;
                        if (field.type === FilterType.TEXT) {
                            ffield.value = v;
                        } else if (field.type === FilterType.TYPEAHEAD) {
                            field.queries.forEach((query: FilterQuery) => {
                                if (query.id === v) {
                                    ffield.query = query;
                                    ffield.value = query.value;
                                }
                            });
                        }
                        this.filterConfig.appliedFilters.push(ffield);
                        this.appliedFilters.push(ffield);
                    });
                }

                // Show filters if the param is configured in filters and it's not
                // in the defaults
                if (DefaultParams.params[key] === undefined) {
                    this.showFilter = true;
                }
            }
        }
    }

    private getBasePath(): string {
        const path = this.location.path();
        return path.replace(/\?.*$/, '');
    }

    private getFilterField(id: string): FilterField {
        let result: FilterField = null;
        this.filterConfig.fields.forEach((item: FilterField) => {
            if (item.id === id) {
                result = item;
            }
        });
        return result;
    }

    private getFilterFieldQuery(
        field: FilterField,
        value: string,
    ): FilterQuery {
        let result: FilterQuery = null;
        field.queries.forEach((item: FilterQuery) => {
            if (item.id === value) {
                result = item;
            }
        });
        return result;
    }

    private addToFilter(filter: Filter) {
        let filterExists = false;
        this.appliedFilters.forEach((item: Filter) => {
            if (
                item.field.id === filter.field.id &&
                item.value === filter.value
            ) {
                filterExists = true;
            }
        });
        if (!filterExists) {
            this.appliedFilters.push(JSON.parse(JSON.stringify(filter)));
        }
    }

    private setUrlParams(params: any) {
        let paramString = '';
        for (const key of Object.keys(params)) {
            paramString += key + '=' + params[key] + '&';
        }

        // Remove trailing '&'
        paramString = paramString.substring(0, paramString.length - 1);
        this.location.replaceState(this.getBasePath(), paramString); // update browser URL
    }

    private prepareContent(data: Content[], count: number) {
        this.contentCount = count;
        const datePattern = /^\d{4}.*$/;
        data.forEach(item => {
            if (item.imported === null) {
                item.imported = 'NA';
            } else if (datePattern.exec(item.imported) !== null) {
                item.imported = moment(item.imported).fromNow();
            }
            item['repository_format'] =
                item.summary_fields['repository']['format'];
            item['avatar_url'] =
                item.summary_fields['namespace']['avatar_url'] ||
                '/assets/avatar.png';
            if (!item.summary_fields['namespace']['is_vendor']) {
                // always show namespace name for community contributors
                item['namespace_name'] =
                    item.summary_fields['namespace']['name'];
            } else {
                // for vendors, assume name is in logo
                item['namespace_name'] = item.summary_fields['namespace'][
                    'avatar_url'
                ]
                    ? ''
                    : item.summary_fields['namespace']['name'];
            }
            item['displayNamespace'] = item.summary_fields['namespace']['name'];
            if (PluginTypes[item.summary_fields['content_type']['name']]) {
                item['iconClass'] = ContentTypesIconClasses.plugin;
            } else {
                item['iconClass'] =
                    ContentTypesIconClasses[
                        item.summary_fields['content_type']['name']
                    ];
            }
            // Determine navigation for item click
            const namespace = item.summary_fields['namespace'][
                'name'
            ].toLowerCase();
            const repository = item.summary_fields['repository'][
                'name'
            ].toLowerCase();
            const name = item.name.toLowerCase();
            item['contentLink'] = `/${namespace}/${repository}`;
            if (item['repository_format'] === RepoFormats.multi) {
                item['contentLink'] += `/${name}`;
            }
        });
        this.contentItems = data;
        this.filterConfig.resultsCount = count;
        this.paginationConfig.totalItems = count;
        if (!count) {
            this.emptyStateConfig.title = this.noResultsState;
        }
    }

    private getFilterConfigFieldIdx(id: string): number {
        let result = null;
        this.filterConfig.fields.forEach((fld: SortField, idx: number) => {
            if (fld.id === id) {
                result = idx;
            }
        });
        return result;
    }

    private preparePlatforms(platforms: Platform[]): void {
        // Add Platforms to filterConfig
        const idx = this.getFilterConfigFieldIdx('platforms');
        if (idx !== null) {
            const platformMap = {};
            platforms.forEach(platform => {
                platformMap[platform.name] = true;
            });
            this.toolbarConfig.filterConfig.fields[idx].queries = [];
            for (const key in platformMap) {
                if (platformMap.hasOwnProperty(key)) {
                    this.toolbarConfig.filterConfig.fields[idx].queries.push({
                        id: key,
                        value: key,
                    });
                }
            }
        }
    }

    private prepareContentTypes(contentTypes: ContentType[]): void {
        // Add Content Types to filterConfig
        const idx = this.getFilterConfigFieldIdx('content_type');
        if (idx !== null) {
            const contentTypeMap = {};
            contentTypes.forEach(ct => {
                if (ct.name === ContentTypes.apb) {
                    contentTypeMap[ct.name] = 'APB';
                } else {
                    contentTypeMap[ct.name] = ct.description;
                }
            });
            this.toolbarConfig.filterConfig.fields[idx].queries = [];
            for (const key in contentTypeMap) {
                if (contentTypeMap.hasOwnProperty(key)) {
                    this.toolbarConfig.filterConfig.fields[idx].queries.push({
                        id: key,
                        value: contentTypeMap[key],
                    });
                }
            }
        }
    }

    private prepareCloudPlatforms(contentTypes: CloudPlatform[]): void {
        // Add Cloud Platforms to filterConfig
        const idx = this.getFilterConfigFieldIdx('cloud_platforms');
        if (idx !== null) {
            const cpMap = {};
            contentTypes.forEach(cp => {
                cpMap[cp.name] = cp.description;
            });
            this.toolbarConfig.filterConfig.fields[idx].queries = [];
            for (const key in cpMap) {
                if (cpMap.hasOwnProperty(key)) {
                    this.toolbarConfig.filterConfig.fields[idx].queries.push({
                        id: key,
                        value: cpMap[key],
                    });
                }
            }
        }
    }

    private setSortConfig(params: any) {
        const fields: SortField[] = [
            {
                id: 'relevance',
                title: 'Best Match',
                sortType: 'numeric',
            },
            {
                id: 'namespace__name,name',
                title: 'Contributor Name',
                sortType: 'alpha',
            },
            {
                id: 'repository__download_count',
                title: 'Download Count',
                sortType: 'numeric',
            },
            {
                id: 'repository__forks_count',
                title: 'Forks',
                sortType: 'numeric',
            },
            {
                id: 'repository__stargazers_count',
                title: 'Stars',
                sortType: 'numeric',
            },
            {
                id: 'repository__watchers_count',
                title: 'Watchers',
                sortType: 'numeric',
            },
        ] as SortField[];

        if (params['order_by'] === undefined) {
            params['order_by'] = '-relevance';
        }

        const result: SortField[] = [] as SortField[];

        // Set ascending
        this.sortConfig.isAscending = true;
        if (params['order_by'].startsWith('-')) {
            this.sortConfig.isAscending = false;
        }

        // Put the requested orderby field at the top of the list
        const order = params['order_by'].replace(/^[+-]/, '');
        fields.forEach(f => {
            if (f.id === order) {
                result.push(f);
            }
        });
        fields.forEach(f => {
            if (f.id !== order) {
                result.push(f);
            }
        });
        this.sortConfig.fields = result;
    }
}
