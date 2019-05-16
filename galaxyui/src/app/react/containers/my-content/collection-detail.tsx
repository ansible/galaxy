import * as React from 'react';

import { CollectionList } from '../../../resources/collections/collection';
import { CollectionListService } from '../../../resources/collections/collection.service';

import { Injector } from '@angular/core';

import { BsModalService } from 'ngx-bootstrap';

import { Namespace } from '../../../resources/namespaces/namespace';

import { AppliedFilter } from '../../shared-types/pf-toolbar';

import { CollectionListItem } from '../../components/my-content/collection-list-item';

import { AddContentModalComponent } from '../../../my-content/add-content-modal/add-content-modal.component';

import { ListView } from 'patternfly-react';

interface IProps {
    injector: Injector;
    namespace: Namespace;
    items: CollectionList[];
    collectionCount: number;
}

export class CollectionDetail extends React.Component<IProps, {}> {
    collectionListService: CollectionListService;
    modalService: BsModalService;
    appliedFilters: AppliedFilter[] = [];

    constructor(props) {
        super(props);

        const { injector } = this.props;

        this.collectionListService = injector.get(CollectionListService);
        this.modalService = injector.get(BsModalService);
    }

    render() {
        return (
            <div className='my-content-wrapper'>
                <ListView>
                    {this.props.items.length > 0 ? (
                        <div className='type-heading'>
                            Collections{' '}
                            <div className='counter'>
                                {this.props.collectionCount}
                            </div>
                        </div>
                    ) : null}

                    {this.props.items.map(collection => {
                        return (
                            <CollectionListItem
                                namespace={this.props.namespace}
                                key={collection.id}
                                collection={collection}
                                handleAction={(event, col) =>
                                    this.handleItemAction(event, col)
                                }
                            />
                        );
                    })}
                </ListView>
            </div>
        );
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
}
