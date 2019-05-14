import { Namespace } from '../../../resources/namespaces/namespace';
import { Injector } from '@angular/core';

import * as React from 'react';
import { ContentType } from '../../shared-types/my-content';
import { RepoDetail } from './repo-detail';
import { CollectionDetail } from './collection-detail';
import { PaginatedRepoCollection } from '../../../resources/combined/combined';

import { RepoCollectionListService } from '../../../resources/combined/combined.service';
import { ContentToolbar } from '../../components/my-content/content-toolbar';

import { CollectionList } from '../../../resources/collections/collection';
import { Repository } from '../../../resources/repositories/repository';
import { AppliedFilter } from '../../shared-types/pf-toolbar';
import { ContentList } from '../../components/my-content/content-list';

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
                <CollectionDetail
                    injector={injector}
                    namespace={namespace}
                    items={collections}
                />
            </ContentList>
        );
    }

    componentDidMount() {
        if (this.props.namespace.active) {
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

        query['order_by'] = this.sortBy;

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
