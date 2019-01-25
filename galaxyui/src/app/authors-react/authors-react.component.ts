import { Component, OnInit } from '@angular/core';

import { ActivatedRoute } from '@angular/router';

import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterType } from 'patternfly-ng/filter/filter-type';
import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';
import { SortConfig } from 'patternfly-ng/sort/sort-config';
import { SortEvent } from 'patternfly-ng/sort/sort-event';

import { Namespace } from '../resources/namespaces/namespace';
import { NamespaceService } from '../resources/namespaces/namespace.service';
import { PFBodyService } from '../resources/pf-body/pf-body.service';

import CommunityRenderer from './react-components/community';

import { Injector } from '@angular/core';

import { Subject } from 'rxjs';

import {
    ContentTypes,
    ContentTypesIconClasses,
    ContentTypesPluralChoices,
} from '../enums/content-types.enum';

@Component({
    selector: 'app-authors',
    templateUrl: './authors-react.component.html',
    styleUrls: ['./authors-react.component.less'],
})
export class AuthorsReactComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'AuthorsReactComponent';

    constructor(
        private route: ActivatedRoute,
        private namespaceService: NamespaceService,
        private pfBody: PFBodyService,
        public injector: Injector,
    ) {}

    pageTitle = 'Community Authors: REACT EDITION';
    pageIcon = 'fa fa-users';
    items: Namespace[] = [];

    filterConfig: FilterConfig;
    sortConfig: SortConfig;
    paginationConfig: PaginationConfig;
    sortBy = 'name';
    filterBy: any = {
        is_vendor: false,
    };
    pageNumber = 1;
    pageSize = 10;
    state = new Subject();

    ngOnInit() {
        this.pfBody.scrollToTop();

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
            appliedFilters: [] as Filter[],
        } as FilterConfig;

        this.sortConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    sortType: 'alpha',
                },
                {
                    id: 'description',
                    title: 'Description',
                    sortType: 'alpha',
                },
            ],
            isAscending: true,
        } as SortConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0,
        } as PaginationConfig;

        const pageConfig = {
            pageIcon: this.pageIcon,
            headerTitle: this.pageTitle,
            filterConfig: this.filterConfig,
            sortConfig: this.sortConfig,
        };

        CommunityRenderer.init(
            pageConfig,
            this.injector,
            i => this.filterChanged(i),
            i => this.sortChanged(i),
            this.state,
            i => this.handlePageSizeChange(i),
            i => this.handlePageNumberChange(i),
        );

        this.route.data.subscribe(data => {
            this.items = data['namespaces']['results'];
            this.paginationConfig.totalItems = data['namespaces']['count'];
            this.prepareNamespaces();
            this.state.next({
                content: this.items,
                paginationConfig: this.paginationConfig,
                loading: false,
            });
        });
    }

    filterChanged($event): void {
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach(filter => {
                if (filter.field.type === 'typeahead') {
                    this.filterBy['or__' + filter.field.id + '__icontains'] =
                        filter.query.id;
                } else {
                    this.filterBy['or__' + filter.field.id + '__icontains'] =
                        filter.value;
                }
            });
        } else {
            this.filterBy = {
                is_vendor: false,
            };
        }
        this.pageNumber = 1;
        this.searchNamespaces();
    }

    sortChanged($event: SortEvent): void {
        if ($event.isAscending) {
            this.sortBy = $event.field.id;
        } else {
            this.sortBy = '-' + $event.field.id;
        }
        this.searchNamespaces();
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.paginationConfig.pageSize = this.pageSize;
            this.pageNumber = 1;
            this.searchNamespaces();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            if (this.pageSize === this.paginationConfig.pageSize) {
                // changed pageNumber without changing pageSize
                this.searchNamespaces();
                this.pfBody.scrollToTop();
            }
        }
    }

    // private

    private prepareNamespaces(): void {
        if (this.items) {
            this.items.forEach(item => {
                if (!item.avatar_url) {
                    item.avatar_url = '/assets/avatar.png';
                }

                // Creat an array of {'Content Type': {count: <int>, iconClass: 'icon-class'}}
                const contentCounts = [];
                for (const ct in ContentTypes) {
                    if (ContentTypes.hasOwnProperty(ct)) {
                        if (ct === ContentTypes.plugin) {
                            // summarize plugins
                            let count = 0;
                            const countObj = {};
                            for (const count_key in item['summary_fields'][
                                'content_counts'
                            ]) {
                                if (
                                    item['summary_fields'][
                                        'content_counts'
                                    ].hasOwnProperty(count_key)
                                ) {
                                    if (count_key.indexOf('plugin') > -1) {
                                        count +=
                                            item['summary_fields'][
                                                'content_counts'
                                            ][count_key];
                                    }
                                }
                            }
                            if (count > 0) {
                                countObj['title'] =
                                    ContentTypesPluralChoices[ct];
                                countObj['count'] = count;
                                countObj['iconClass'] =
                                    ContentTypesIconClasses[ct];
                                contentCounts.push(countObj);
                            }
                        } else if (
                            item['summary_fields']['content_counts'][
                                ContentTypes[ct]
                            ] > 0
                        ) {
                            const countObj = {};
                            countObj['title'] = ContentTypesPluralChoices[ct];
                            countObj['count'] =
                                item['summary_fields']['content_counts'][
                                    ContentTypes[ct]
                                ];
                            countObj['iconClass'] = ContentTypesIconClasses[ct];
                            contentCounts.push(countObj);
                        }
                    }
                }
                item['contentCounts'] = contentCounts;
            });
        }
    }

    private searchNamespaces() {
        this.state.next({ loading: true });
        this.filterBy['page_size'] = this.pageSize;
        this.filterBy['page'] = this.pageNumber;
        this.filterBy['order'] = this.sortBy;
        this.namespaceService.pagedQuery(this.filterBy).subscribe(result => {
            this.items = result.results as Namespace[];
            this.prepareNamespaces();
            this.filterConfig.resultsCount = result.count;
            this.paginationConfig.totalItems = result.count;
            this.state.next({
                content: this.items,
                paginationConfig: this.paginationConfig,
                loading: false,
            });
        });
    }
}
