import { Namespace } from '../../../resources/namespaces/namespace';
import { Injector } from '@angular/core';

import * as React from 'react';
import { RepoDetail } from './repo-detail';
import { CollectionDetail } from './collection-detail';
import { PaginatedRepoCollection } from '../../../resources/combined/combined';

import { RepoCollectionListService } from '../../../resources/combined/combined.service';

import { CollectionList } from '../../../resources/collections/collection';
import { Repository } from '../../../resources/repositories/repository';
import { AppliedFilter } from '../../shared-types/pf-toolbar';
import { ContentList } from '../../components/my-content/content-list';
import { interval, Subscription } from 'rxjs';

import { cloneDeep } from 'lodash';

interface IProps {
    namespace: Namespace;
    injector: Injector;
}

interface IState {
    loading: boolean;
    collectionCount: number;
    repoCount: number;
    page: number;
    pageSize: number;
    repos: Repository[];
    collections: CollectionList[];
}

export class ContentDetailContainer extends React.Component<IProps, IState> {
    repoCollectionListService: RepoCollectionListService;
    sortBy = 'name';
    appliedFilters: AppliedFilter[] = [];
    polling: Subscription;
    pollingEnabled = false;

    constructor(props) {
        super(props);

        this.repoCollectionListService = this.props.injector.get(
            RepoCollectionListService,
        );

        this.state = {
            loading: true,
            collectionCount: 0,
            repoCount: 0,
            page: 1,
            pageSize: 10,
            repos: [],
            collections: [],
        };
    }

    render() {
        const {
            loading,
            repoCount,
            collectionCount,
            collections,
            repos,
            pageSize,
            page,
        } = this.state;
        const { namespace, injector } = this.props;
        return (
            <ContentList
                itemCount={repoCount + collectionCount}
                loading={loading}
                pageSize={pageSize}
                pageNumber={page}
                namespace={namespace}
                setPageSize={x => this.setPageSize(x)}
                setPageNumber={x => this.setPageNumber(x)}
                handleSortChange={x => this.handleSortChange(x)}
                handleFilterChange={x => this.handleFilterChange(x)}
            >
                {collectionCount > 0 ? (
                    <CollectionDetail
                        injector={injector}
                        namespace={namespace}
                        items={collections}
                        collectionCount={collectionCount}
                        refreshContent={() => this.loadData()}
                        setToLoading={x => this.toggleLoadingForCollection(x)}
                    />
                ) : null}

                {repoCount > 0 ? (
                    <RepoDetail
                        injector={injector}
                        namespace={namespace}
                        items={repos}
                        repoCount={repoCount}
                        setToLoading={x => this.toggleLoadingForRepo(x)}
                        refreshContent={() => this.loadData()}
                        setPolling={x => (this.pollingEnabled = x)}
                    />
                ) : null}
            </ContentList>
        );
    }

    componentDidMount() {
        if (this.props.namespace.active) {
            this.loadData();

            if (this.props.namespace.active) {
                this.polling = interval(10000).subscribe(() => {
                    this.pollData();
                });
            }
        }
    }

    componentWillUnmount() {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    private toggleLoadingForRepo(repo: Repository) {
        const items = cloneDeep(this.state.repos);
        const repoInd = items.findIndex(x => x.id === repo.id);

        items[repoInd].summary_fields.loading = true;

        this.setState({ repos: items });
    }

    private toggleLoadingForCollection(collection: CollectionList) {
        const items = cloneDeep(this.state.collections);
        const ind = items.findIndex(x => x.id === collection.id);

        // I should make this an actual property of the CollectionList object...
        items[ind]['loading'] = true;

        this.setState({ collections: items });
    }

    private pollData() {
        if (this.pollingEnabled) {
            this.loadData();
        }
    }

    private handleSortChange(event) {
        if (event.isAscending) {
            this.sortBy = event.field.id;
        } else {
            this.sortBy = '-' + event.field.id;
        }
        this.setState({ loading: true, page: 1 }, () => this.loadData());
    }

    private handleFilterChange(event) {
        this.appliedFilters = event.appliedFilters;
        this.setState({ loading: true, page: 1 }, () => this.loadData());
    }

    private setPageSize(i) {
        this.setState({ pageSize: i, loading: true }, () => this.loadData());
    }

    private setPageNumber(i) {
        this.setState({ page: i, loading: true }, () => this.loadData());
    }

    private loadData() {
        const query = {
            namespace: this.props.namespace.name,
            page_size: this.state.pageSize,
            page: this.state.page,
        };

        for (const filter of this.appliedFilters) {
            query[filter.field.id] = filter.value;
        }

        query['order'] = this.sortBy;

        this.repoCollectionListService
            .query(query)
            .subscribe((result: PaginatedRepoCollection) => {
                this.setState({
                    collections: result.collection.results,
                    collectionCount: result.collection.count,
                    repos: result.repository.results,
                    repoCount: result.repository.count,
                    loading: false,
                });
            });
    }
}
