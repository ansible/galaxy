import * as React from 'react';

import { ActivatedRoute } from '@angular/router';

import { PaginationConfig } from '../components/patternfly-pager';
import {
    FilterConfig,
    FilterOption,
    AppliedFilter,
    SortConfig,
} from '../shared-types/pf-toolbar';

import CommunityComponent from '../components/community';

import { Namespace } from '../../resources/namespaces/namespace';
import { NamespaceService } from '../../resources/namespaces/namespace.service';
import { PFBodyService } from '../../resources/pf-body/pf-body.service';

import { Injector } from '@angular/core';

import {
    ContentTypes,
    ContentTypesIconClasses,
    ContentTypesPluralChoices,
} from '../../enums/content-types.enum';

interface IProps {
    injector: Injector;
}

interface IState {
    items: Namespace[];
    paginationConfig: PaginationConfig;
    loading: boolean;
    filterConfig: FilterConfig;
}

export class CommunityPage extends React.Component<IProps, IState> {
    // Static
    route: ActivatedRoute;
    namespaceService: NamespaceService;
    pfBody: PFBodyService;
    pageIcon = 'fa fa-users';
    pageTitle = 'Community Authors';
    sortConfig: SortConfig;

    sortBy = 'name';
    filterBy = { is_vendor: false };
    pageNumber = 1;
    pageSize = 10;

    constructor(props) {
        super(props);

        this.state = {
            items: [],
            paginationConfig: {
                pageSize: 10,
                pageNumber: 1,
                totalItems: 0,
            } as PaginationConfig,
            loading: true,
            filterConfig: {
                fields: [
                    {
                        id: 'name',
                        title: 'Name',
                        placeholder: 'Filter by Name...',
                        type: 'text',
                    },
                    {
                        id: 'description',
                        title: 'Description',
                        placeholder: 'Filter by Description...',
                        type: 'text',
                    },
                ] as FilterOption[],
                resultsCount: 0,
                appliedFilters: [] as AppliedFilter[],
            } as FilterConfig,
        };

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
    }

    componentDidMount() {
        this.route = this.props.injector.get(ActivatedRoute);
        this.namespaceService = this.props.injector.get(NamespaceService);
        this.pfBody = this.props.injector.get(PFBodyService);

        this.pfBody.scrollToTop();

        this.route.data.subscribe(data => {
            let items = data['namespaces']['results'];
            items = this.prepareNamespaces(items);

            const paginationConfig = this.state.paginationConfig;
            paginationConfig.totalItems = data['namespaces']['count'];

            this.setState({
                items: items,
                paginationConfig: paginationConfig,
                loading: false,
            });
        });
    }

    render() {
        return (
            <CommunityComponent
                headerIcon={this.pageIcon}
                headerTitle={this.pageTitle}
                filterConfig={this.state.filterConfig}
                sortConfig={this.sortConfig}
                content={this.state.items}
                paginationConfig={this.state.paginationConfig}
                loading={this.state.loading}
                updateFilter={i => this.filterChanged(i)}
                updateSort={i => this.sortChanged(i)}
                updatePageSize={i => this.handlePageSizeChange(i)}
                updatePageNumber={i => this.handlePageNumberChange(i)}
            />
        );
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

    sortChanged($event): void {
        if ($event.isAscending) {
            this.sortBy = $event.field.id;
        } else {
            this.sortBy = '-' + $event.field.id;
        }
        this.searchNamespaces();
    }

    handlePageSizeChange($event) {
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.searchNamespaces();
        }
    }

    handlePageNumberChange($event) {
        if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            this.searchNamespaces();
            this.pfBody.scrollToTop();
        }
    }

    // private

    private prepareNamespaces(items): Namespace[] {
        if (items) {
            items.forEach(item => {
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

        return items;
    }

    private searchNamespaces() {
        this.setState({ loading: true });

        this.filterBy['page_size'] = this.pageSize;
        this.filterBy['page'] = this.pageNumber;
        this.filterBy['order'] = this.sortBy;

        this.namespaceService.pagedQuery(this.filterBy).subscribe(result => {
            const items = this.prepareNamespaces(result.results);

            const filterConfig = this.state.filterConfig;
            const paginationConfig = this.state.paginationConfig;

            paginationConfig.totalItems = result.count;
            paginationConfig.pageNumber = this.pageNumber;
            paginationConfig.pageSize = this.pageSize;
            filterConfig.resultsCount = result.count;

            this.setState({
                items: items,
                paginationConfig: paginationConfig,
                filterConfig: filterConfig,
                loading: false,
            });
        });
    }
}
