import * as React from 'react';

import { CollectionList } from '../../../resources/collections/collection';
import { CollectionListService } from '../../../resources/collections/collection.service';

import { ContentToolbar } from '../../components/my-content/content-toolbar';
import { ContentType } from '../../shared-types/my-content';

import { Injector } from '@angular/core';

import { BsModalService } from 'ngx-bootstrap';

import { Namespace } from '../../../resources/namespaces/namespace';
import { PagedResponse } from '../../../resources/paged-response';

import { AppliedFilter } from '../../shared-types/pf-toolbar';

import { CollectionListItem } from '../../components/my-content/collection-list-item';
import { ContentList } from '../../components/my-content/content-list';

import { AddContentModalComponent } from '../../../my-content/add-content-modal/add-content-modal.component';

interface IProps {
    displayedType: ContentType;
    injector: Injector;
    namespace: Namespace;

    contentAdded?: boolean;
    setDisplayedType: (x: ContentType) => void;
}

interface IState {
    items: CollectionList[];
    loading: boolean;
    numberOfResults: number;
    page: number;
    pageSize: number;
}

export class CollectionDetail extends React.Component<IProps, IState> {
    collectionListService: CollectionListService;
    modalService: BsModalService;
    appliedFilters: AppliedFilter[] = [];
    sortBy: string = 'name';

    constructor(props) {
        super(props);

        const { injector } = this.props;

        this.collectionListService = injector.get(CollectionListService);
        this.modalService = injector.get(BsModalService);

        this.state = {
            items: [],
            loading: true,
            numberOfResults: 0,
            page: 1,
            pageSize: 10,
        };
    }

    render() {
        return (
            <div className='my-content-wrapper'>
                <ContentToolbar
                    displayedType={this.props.displayedType}
                    onSortChange={x => this.handleSortChange(x)}
                    onFilterChange={x => this.handleFilterChange(x)}
                    setDisplayedType={this.props.setDisplayedType}
                    numberOfResults={0}
                />
                <ContentList
                    emptyStateText='No Collections'
                    itemCount={this.state.numberOfResults}
                    loading={this.state.loading}
                    namespace={this.props.namespace}
                    pageSize={this.state.pageSize}
                    pageNumber={this.state.page}
                    setPageSize={x => this.setPageSize(x)}
                    setPageNumber={x => this.setPageNumber(x)}
                >
                    {this.state.items.map(collection => {
                        return (
                            <CollectionListItem
                                namespace={this.props.namespace}
                                key={collection.id}
                                collection={collection}
                                handleAction={(event, collection) =>
                                    this.handleItemAction(event, collection)
                                }
                            />
                        );
                    })}
                </ContentList>
            </div>
        );
    }

    componentDidMount() {
        if (this.props.namespace.active) {
            this.loadCollections();
        }
    }

    private handleSortChange(event) {
        if (event.isAscending) {
            this.sortBy = event.field.id;
        } else {
            this.sortBy = '-' + event.field.id;
        }
        this.setState({ loading: true, page: 1 }, () => this.loadCollections());
    }

    private handleFilterChange(event) {
        this.appliedFilters = event.appliedFilters;
        this.setState({ loading: true, page: 1 }, () => this.loadCollections());
    }

    private setPageSize(i) {
        this.setState({ pageSize: i, loading: true }, () =>
            this.loadCollections(),
        );
    }

    private setPageNumber(i) {
        this.setState({ page: i, loading: true }, () => this.loadCollections());
    }

    private handleItemAction(event, collection): void {
        switch (event) {
            case 'import':
                this.importCollection(collection);
                break;
            case 'deprecate':
                this.deprecate(true, collection);
                break;
            case 'undeprecate':
                this.deprecate(false, collection);
                break;
        }
    }

    private deprecate(isDeprecated, collection) {
        // Todo once API is available
        console.log('Set deprection status for ' + collection.name);
    }

    private importCollection(collection) {
        const initialState = {
            namespace: this.props.namespace,
            collectionName: collection.name,
        };
        this.modalService.show(AddContentModalComponent, {
            initialState: initialState,
            keyboard: true,
            animated: true,
        });
    }

    private loadCollections() {
        const query = {
            namespace: this.props.namespace.id,
            page_size: this.state.pageSize,
            page: this.state.page,
        };

        for (const filter of this.appliedFilters) {
            query[`or__${filter.field.id}__icontains`] = filter.value;
        }

        query['order_by'] = this.sortBy;

        this.collectionListService
            .pagedQuery(query)
            .subscribe((result: PagedResponse) => {
                const collections: CollectionList[] = result.results;

                this.setState({
                    items: collections,
                    loading: false,
                    numberOfResults: result.count,
                });
            });
    }
}
