import { Component, Input, OnInit } from '@angular/core';

import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';

import { Content } from '../../../resources/content/content';
import { ContentService } from '../../../resources/content/content.service';
import { Repository } from '../../../resources/repositories/repository';

import { ContentTypes } from '../../../enums/content-types.enum';

import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterEvent } from 'patternfly-ng/filter/filter-event';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterType } from 'patternfly-ng/filter/filter-type';

import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';

import { forkJoin, Observable } from 'rxjs';

@Component({
    selector: 'roles-detail',
    templateUrl: './roles.component.html',
    styleUrls: ['./roles.component.less'],
})
export class RolesComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'RolesComponent';

    constructor(private contentService: ContentService) {}

    filterConfig: FilterConfig;
    listConfig: ListConfig;
    paginationConfig: PaginationConfig;
    pageSize = 10;
    pageNumber = 1;
    query: string;
    items: Content[] = [];
    loading: Boolean = true;
    _roles: Content[];
    _repository: Repository;
    _selectedContent: Content;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    @Input()
    set selectedContent(data: Content) {
        if (data && data.content_type === ContentTypes.role) {
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
            ] as FilterField[],
            resultsCount: 0,
            appliedFilters: [],
        } as FilterConfig;

        if (this._selectedContent) {
            this.filterConfig.appliedFilters.push({
                field: this.filterConfig.fields[0],
                value: this._selectedContent.name,
            } as Filter);
        }

        this.queryContentList(
            this.selectedContent ? this.selectedContent.name : null,
        );
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
                params.push(
                    `or__${
                        filter.field.id
                    }__icontains=${filter.value.toLowerCase()}`,
                );
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
            content_type__name: ContentTypes.role,
            repository__id: this.repository.id,
        };
        if (contentName) {
            params['name'] = contentName;
        }
        const _tmp = [];
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                _tmp.push(`${key}=${params[key]}`);
            }
        }
        queryString +=
            queryString === '?' ? _tmp.join('&') : '&' + _tmp.join('&');
        this.contentService.pagedQuery(queryString).subscribe(results => {
            this._roles = results.results as Content[];
            this.filterConfig.resultsCount = results.count;
            this.paginationConfig.totalItems = results.count;
            this.getContentDetail();
        });
    }

    private getContentDetail() {
        if (!this._roles || !this._roles.length) {
            this.items = [];
            this.loading = false;
            return;
        }

        const queries: Observable<Content>[] = [];
        this._roles.forEach((role: Content) => {
            queries.push(this.contentService.get(role.id));
        });

        forkJoin(queries).subscribe((results: Content[]) => {
            this.items = JSON.parse(JSON.stringify(results));
            this.items.forEach(item => {
                item['install_cmd'] = `mazer install ${
                    item.summary_fields['namespace']['name']
                }.${item.summary_fields['repository']['name']}`;
                item['hasTags'] = false;
                if (
                    item.summary_fields['tags'] &&
                    item.summary_fields['tags'].length
                ) {
                    item['tags'] = item.summary_fields['tags'];
                    item['hasTags'] = true;
                }
                ['dependencies', 'platforms', 'cloud_platforms'].forEach(
                    key => {
                        item[key] = [];
                        if (item.summary_fields[key]) {
                            item[key] = item.summary_fields[key];
                        }
                    },
                );
            });
            this.loading = false;
        });
    }
}
