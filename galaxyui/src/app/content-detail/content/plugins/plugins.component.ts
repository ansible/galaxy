import { Component, Input, OnInit } from '@angular/core';

import { EmptyStateConfig } from 'patternfly-ng/empty-state/empty-state-config';

import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';

import { Content } from '../../../resources/content/content';
import { ContentService } from '../../../resources/content/content.service';
import { Repository } from '../../../resources/repositories/repository';

import { ContentTypes } from '../../../enums/content-types.enum';

import { PluginNames, PluginTypes } from '../../../enums/plugin-types.enum';

import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterEvent } from 'patternfly-ng/filter/filter-event';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterType } from 'patternfly-ng/filter/filter-type';

import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';

import { forkJoin, Observable } from 'rxjs';

@Component({
    selector: 'plugins-detail',
    templateUrl: './plugins.component.html',
    styleUrls: ['./plugins.component.less'],
})
export class PluginsComponent implements OnInit {
    constructor(private contentService: ContentService) {}

    emptyStateConfig: EmptyStateConfig;
    filterConfig: FilterConfig;
    listConfig: ListConfig;
    paginationConfig: PaginationConfig;
    pageSize = 10;
    pageNumber = 1;
    query: string;
    items: Content[] = [];
    loading: Boolean = true;
    _plugins: Content[];
    _repository: Repository;
    _selectedContent: Content;

    PluginNames: typeof PluginNames = PluginNames;
    PluginTypes: typeof PluginTypes = PluginTypes;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    @Input()
    set selectedContent(data: Content) {
        if (data && data.content_type.indexOf('plugin') > -1) {
            this._selectedContent = data;
            if (this.filterConfig && this.filterConfig.fields) {
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[0],
                    value: this._selectedContent.name,
                } as Filter);
                this.queryContentList(this._selectedContent.name);
            }
        }
    }

    get selectedContent(): Content {
        return this._selectedContent;
    }

    ngOnInit() {
        this.emptyStateConfig = {
            iconStyleClass: 'pficon-warning-triangle-o',
            info: 'This plugin does not contain any documentation or metadata.',
            title: 'No Metadata Found',
        } as EmptyStateConfig;

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: false,
            showCheckbox: false,
            useExpandItems: true,
        } as ListConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0,
        } as PaginationConfig;

        this.filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: FilterType.TEXT,
                },
                {
                    id: 'description',
                    title: 'Description',
                    placeholder: 'Filter by Description...',
                    type: FilterType.TEXT,
                },
                {
                    id: 'plugin_type',
                    title: 'Plugin Type',
                    placeholder: 'Plugin Type',
                    type: FilterType.TYPEAHEAD,
                    queries: [],
                },
            ] as FilterField[],
            resultsCount: 0,
            appliedFilters: [],
        } as FilterConfig;

        for (const key in PluginTypes) {
            if (PluginTypes.hasOwnProperty(key)) {
                this.filterConfig.fields[2].queries.push({
                    id: key,
                    value: PluginTypes[key],
                });
            }
        }

        if (this._selectedContent) {
            this.filterConfig.appliedFilters.push({
                field: this.filterConfig.fields[0],
                value: this._selectedContent.name,
            } as Filter);
        }

        this.queryContentList(this.selectedContent ? this.selectedContent.name : null);
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.queryContentList();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            if (this.pageSize === this.paginationConfig.pageSize) {
                // changed pageNumber without changing pageSize
                this.queryContentList();
            }
        }
    }

    applyFilters($event: FilterEvent) {
        const params: string[] = [];
        let query: string = null;
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach((filter: Filter) => {
                if (filter.field.id === 'name' || filter.field.id === 'description') {
                    params.push(`or__${filter.field.id}__icontains=${filter.value.toLowerCase()}`);
                } else if (filter.field.id === 'plugin_type') {
                    params.push(`content_type__name=${filter.value.toLowerCase().replace(' ', '_')}`);
                }
            });
            query = '?' + params.join('&');
        }
        this.query = query;
        this.queryContentList();
    }

    // private

    private queryContentList(contentName?: string) {
        this.loading = true;
        let queryString = this.query ? this.query : '?';
        const params = {
            page_size: this.pageSize,
            page: this.pageNumber,
            repository__id: this.repository.id,
        };
        if (queryString.indexOf('content_type__name') < 0) {
            params['content_type__name__icontains'] = ContentTypes.plugin;
        }
        if (contentName) {
            params['name'] = contentName;
        }
        const _tmp = [];
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                _tmp.push(`${key}=${params[key]}`);
            }
        }
        queryString += queryString === '?' ? _tmp.join('&') : '&' + _tmp.join('&');
        this.contentService.pagedQuery(queryString).subscribe(results => {
            this._plugins = results.results as Content[];
            this.filterConfig.resultsCount = results.count;
            this.paginationConfig.totalItems = results.count;
            this.getContentDetail();
        });
    }

    private getContentDetail() {
        if (!this._plugins || !this._plugins.length) {
            this.items = [];
            this.loading = false;
            return;
        }

        const queries: Observable<Content>[] = [];
        this._plugins.forEach((plugin: Content) => {
            queries.push(this.contentService.get(plugin.id));
        });

        forkJoin(queries).subscribe((results: Content[]) => {
            this.items = JSON.parse(JSON.stringify(results));
            this.items.forEach(item => {
                if (!item.description) {
                    if (item.metadata && item.metadata['documentation']) {
                        item.description = item.metadata['documentation']['short_description'];
                    }
                }
            });
            this.loading = false;
        });
    }
}
