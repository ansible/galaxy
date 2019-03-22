import * as React from 'react';

import { ContentToolbar } from '../../components/my-content/content-toolbar';
import { ContentType } from '../../shared-types/my-content';

import { Repository as VanillaRepo } from '../../../resources/repositories/repository';
import { RepositoryService } from '../../../resources/repositories/repository.service';
import { RepositoryImportService } from '../../../resources/repository-imports/repository-import.service';

import { Injector } from '@angular/core';

import { BsModalRef, BsModalService } from 'ngx-bootstrap';

import { Namespace } from '../../../resources/namespaces/namespace';
import { PagedResponse } from '../../../resources/paged-response';
import { ProviderNamespace } from '../../../resources/provider-namespaces/provider-namespace';

import { interval, Subscription } from 'rxjs';

import * as moment from 'moment';

import { AppliedFilter } from '../../shared-types/pf-toolbar';

import { RepoListItem } from '../../components/my-content/repo-list-item';
import { ContentList } from '../../components/my-content/content-list';

import { cloneDeep } from 'lodash';

class Repository extends VanillaRepo {
    expanded: boolean;
}

interface IProps {
    displayedType: ContentType;
    injector: Injector;
    namespace: Namespace;

    contentAdded?: boolean;
    setDisplayedType: (x: ContentType) => void;
}

interface IState {
    items: Repository[];
    loading: boolean;
    numberOfResults: number;
    page: number;
    pageSize: number;
}

export class RepoDetail extends React.Component<IProps, IState> {
    repositoryService: RepositoryService;
    repositoryImportService: RepositoryImportService;
    modalService: BsModalService;
    polling: Subscription;
    pollingEnabled = false;
    appliedFilters: AppliedFilter[] = [];
    sortBy = 'name';

    constructor(props) {
        super(props);

        const { injector } = this.props;

        this.repositoryService = injector.get(RepositoryService);
        this.repositoryImportService = injector.get(RepositoryImportService);
        this.modalService = injector.get(BsModalService);

        this.state = {
            items: [],
            loading: true,
            numberOfResults: 0,
            page: 1,
            pageSize: 10,
        };
    }

    componentDidMount() {
        const provider_namespaces = this.props.namespace.summary_fields
            .provider_namespaces;

        if (this.props.namespace.active && provider_namespaces.length) {
            this.polling = interval(10000).subscribe(() => {
                this.pollRepos();
            });

            this.refreshRepositories();
        }

        this.modalService.onHidden.subscribe(_ => {
            this.refreshRepositories();
        });
    }

    render() {
        return (
            <div className='my-content-wrapper'>
                <ContentToolbar
                    displayedType={this.props.displayedType}
                    onSortChange={x => this.handleSortChange(x)}
                    onFilterChange={x => this.handleFilterChange(x)}
                    setDisplayedType={this.props.setDisplayedType}
                    numberOfResults={this.state.numberOfResults}
                />
                <ContentList
                    emptyStateText='No Repositories'
                    itemCount={this.state.numberOfResults}
                    loading={this.state.loading}
                    namespace={this.props.namespace}
                    pageSize={this.state.pageSize}
                    pageNumber={this.state.page}
                    setPageSize={x => this.setPageSize(x)}
                    setPageNumber={x => this.setPageNumber(x)}
                >
                    {this.state.items.map(repo => {
                        return (
                            <RepoListItem
                                namespace={this.props.namespace}
                                key={repo.id}
                                repo={repo}
                                handleAction={(event, r) =>
                                    this.handleItemAction(event, r)
                                }
                            />
                        );
                    })}
                </ContentList>
            </div>
        );
    }

    componentWillUnmount() {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    private setPageSize(i) {
        this.setState({ pageSize: i, loading: true }, () =>
            this.refreshRepositories(),
        );
    }

    private setPageNumber(i) {
        this.setState({ page: i, loading: true }, () =>
            this.refreshRepositories(),
        );
    }

    private handleItemAction(event, repo): void {
        if (repo) {
            switch (event) {
                case 'import':
                    this.importRepository(repo);
                    break;
                case 'delete':
                    this.deleteRepository(repo);
                    break;
                case 'deprecate':
                    this.deprecate(true, repo);
                    break;
                case 'undeprecate':
                    this.deprecate(false, repo);
                    break;
            }
        }
    }

    private deprecate(isDeprecated: boolean, repo: Repository): void {
        repo = cloneDeep(repo);
        repo.deprecated = isDeprecated;

        const items = cloneDeep(this.state.items);
        const repoInd = items.findIndex(x => x.id === repo.id);

        items[repoInd].summary_fields.loading = true;

        this.setState({ items: items }, () => {
            this.repositoryService.save(repo).subscribe(() => {
                this.refreshRepositories();
            });
        });
    }

    private importRepository(repository: Repository) {
        // Start an import
        this.pollingEnabled = true;

        const items = cloneDeep(this.state.items);

        const repoInd = items.findIndex(x => x.id === repository.id);

        items[repoInd]['latest_import']['state'] = 'PENDING';
        items[repoInd]['latest_import']['as_of_dt'] = '';

        this.setState({ items: items }, () =>
            this.repositoryImportService
                .save({ repository_id: repository.id })
                .subscribe(response => {
                    console.log(
                        `Started import for repository ${repository.id}`,
                    );
                }),
        );
    }

    private deleteRepository(repository: Repository) {
        this.repositoryService
            .destroy(repository)
            .subscribe(_ => this.refreshRepositories());
    }

    private handleSortChange(event) {
        if (event.isAscending) {
            this.sortBy = event.field.id;
        } else {
            this.sortBy = '-' + event.field.id;
        }
        this.setState({ loading: true, page: 1 }, () =>
            this.refreshRepositories(),
        );
    }

    private handleFilterChange(event) {
        this.appliedFilters = event.appliedFilters;
        this.setState({ loading: true, page: 1 }, () =>
            this.refreshRepositories(),
        );
    }

    private pollRepos() {
        if (this.pollingEnabled) {
            this.refreshRepositories();
        }
    }

    private refreshRepositories() {
        // Django REST framework allows us to query multiple namespaces by using
        // provider_namespace__id__in=id1,id2,id3
        const query = {
            provider_namespace__id__in: '',
            page_size: this.state.pageSize,
            page: this.state.page,
        };

        for (const filter of this.appliedFilters) {
            query[`or__${filter.field.id}__icontains`] = filter.value;
        }

        query['order_by'] = this.sortBy;

        this.props.namespace.summary_fields.provider_namespaces.forEach(
            (pns: ProviderNamespace) => {
                query.provider_namespace__id__in += pns.id + ',';
            },
        );

        query.provider_namespace__id__in = query.provider_namespace__id__in.slice(
            0,
            -1,
        );

        this.repositoryService
            .pagedQuery(query)
            .subscribe((result: PagedResponse) => {
                const repositories: Repository[] = result.results;

                // // maxItems is used to determine if we need to show the filter or not
                // // it should never go down to avoid hiding the filter by accident when
                // // a query returns a small number of items.
                // if (this.maxItems < this.paginationConfig.totalItems) {
                //     this.maxItems = this.paginationConfig.totalItems;
                // }

                // Collect a list of expanded items to keep them from getting
                // closed when the page refreshes.
                const expanded = [];

                this.state.items.forEach(item => {
                    if (item.expanded) {
                        expanded.push(item.id);
                    }
                });

                // Generate a new list of repos
                const updatedList: Repository[] = [];

                // Only poll imports if there are pending imports
                this.pollingEnabled = false;
                repositories.forEach(repo => {
                    if (
                        repo.summary_fields.latest_import.state === 'PENDING' ||
                        repo.summary_fields.latest_import.state === 'RUNNING'
                    ) {
                        this.pollingEnabled = true;
                    }

                    repo = this.prepareRepository(repo);
                    if (expanded.includes(repo.id)) {
                        repo.expanded = true;
                    }
                    updatedList.push(repo);
                });

                this.setState({
                    items: updatedList,
                    loading: false,
                    numberOfResults: result.count,
                });
            });
    }

    private prepareRepository(item: Repository): Repository {
        item['expanded'] = false;
        item['latest_import'] = {};
        item['detail_url'] = this.getDetailUrl(item);
        item['iconClass'] = this.getIconClass(item.format);
        if (item.summary_fields.latest_import) {
            item['latest_import'] = item.summary_fields.latest_import;
            if (item['latest_import']['finished']) {
                item['latest_import']['as_of_dt'] = moment(
                    item['latest_import']['finished'],
                ).fromNow();
            } else {
                item['latest_import']['as_of_dt'] = moment(
                    item['latest_import']['modified'],
                ).fromNow();
            }
        }

        return item;
    }

    private getDetailUrl(item: Repository) {
        return `/${item.summary_fields['namespace']['name']}/${item.name}`;
    }

    private getIconClass(repository_format: string) {
        let result = 'pficon-repository list-pf-icon list-pf-icon-small';
        switch (repository_format) {
            case 'apb':
                result = 'pficon-bundle list-pf-icon list-pf-icon-small';
                break;
            case 'role':
                result = 'fa fa-gear list-pf-icon list-pf-icon-small';
                break;
        }
        return result;
    }
}
