import { Component, OnInit } from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';

import { ActionConfig } from 'patternfly-ng/action/action-config';
import { EmptyStateConfig } from 'patternfly-ng/empty-state/empty-state-config';
import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterType } from 'patternfly-ng/filter/filter-type';
import { ListEvent } from 'patternfly-ng/list/list-event';
import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';
import { SortConfig } from 'patternfly-ng/sort/sort-config';
import { SortEvent } from 'patternfly-ng/sort/sort-event';
import { ToolbarConfig } from 'patternfly-ng/toolbar/toolbar-config';

import { Namespace } from '../resources/namespaces/namespace';
import { NamespaceService } from '../resources/namespaces/namespace.service';

import {
    ContentTypes,
    ContentTypesIconClasses,
    ContentTypesPluralChoices,
} from '../enums/content-types.enum';

@Component({
    selector: 'app-vendors',
    templateUrl: './vendors.component.html',
    styleUrls: ['./vendors.component.less'],
})
export class VendorsComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'VendorsComponent';

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private namespaceService: NamespaceService,
    ) {}

    pageTitle = 'Partners';
    headerIcon = 'fa fa-star';
    pageLoading = true;
    items: Namespace[] = [];

    emptyStateConfig: EmptyStateConfig;
    toolbarActionConfig: ActionConfig;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
    toolbarConfig: ToolbarConfig;
    paginationConfig: PaginationConfig;
    sortBy = 'name';
    filterBy: any = {
        is_vendor: 'true',
    };
    pageNumber = 1;
    pageSize = 10;

    ngOnInit() {
        this.emptyStateConfig = {
            info: '',
            title: 'No partners match your search',
            iconStyleClass: 'pficon pficon-filter',
        } as EmptyStateConfig;

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

        this.toolbarActionConfig = {
            primaryActions: [],
            moreActions: [],
        } as ActionConfig;

        this.toolbarConfig = {
            actionConfig: this.toolbarActionConfig,
            filterConfig: this.filterConfig,
            sortConfig: this.sortConfig,
            views: [],
        } as ToolbarConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0,
        } as PaginationConfig;

        this.route.data.subscribe(data => {
            this.items = data['vendors']['results'];
            this.paginationConfig.totalItems = data['vendors']['count'];
            this.prepareNamespaces();
        });
    }

    handleListClick($event: ListEvent): void {
        this.router.navigate(['/', $event.item.name]);
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
                is_vendor: 'true',
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
            }
        }
    }

    // private

    private prepareNamespaces(): void {
        if (this.items) {
            this.items.forEach(item => {
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
        this.pageLoading = false;
    }

    private searchNamespaces() {
        this.pageLoading = true;
        this.filterBy['page_size'] = this.pageSize;
        this.filterBy['page'] = this.pageNumber;
        this.filterBy['order'] = this.sortBy;
        this.namespaceService.pagedQuery(this.filterBy).subscribe(result => {
            this.items = result.results as Namespace[];
            this.prepareNamespaces();
            this.filterConfig.resultsCount = result.count;
            this.paginationConfig.totalItems = result.count;
            this.pageLoading = false;
        });
    }
}
