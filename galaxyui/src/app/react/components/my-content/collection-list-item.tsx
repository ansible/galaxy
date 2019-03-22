import * as React from 'react';
import { CollectionList } from '../../../resources/collections/collection';
import { Namespace } from '../../../resources/namespaces/namespace';
import { Link } from '../../lib/link';

import {
    ListView,
    ListViewItem,
    OverlayTrigger,
    Tooltip,
    Button,
    DropdownKebab,
    MenuItem,
} from 'patternfly-react';

import { Score } from '../score';

interface IProps {
    collection: CollectionList;
    namespace: Namespace;
    handleAction: (event, collection: CollectionList) => void;
}

export class CollectionListItem extends React.Component<IProps, {}> {
    render() {
        const { collection, namespace } = this.props;

        return (
            <ListViewItem
                leftContent={
                    <i className='pficon-repository list-pf-icon list-pf-icon-small' />
                }
                key={collection.name}
                heading={
                    <Link
                        to={`/collection/${namespace.name}/${collection.name}`}
                    >
                        {collection.name}
                    </Link>
                }
                additionalInfo={this.renderAdditional(collection)}
                actions={this.renderActions(collection)}
            />
        );
    }

    private renderActions(collection) {
        const { handleAction } = this.props;

        return (
            <div>
                <Button onClick={() => handleAction('import', collection)}>
                    <i className='fa fa-upload' /> Upload New Version
                </Button>
                <DropdownKebab id='repo-actions' pullRight>
                    {collection.deprecated ? (
                        <MenuItem
                            onClick={() =>
                                handleAction('undeprecate', collection)
                            }
                        >
                            Undeprecate
                        </MenuItem>
                    ) : (
                        <MenuItem
                            onClick={() =>
                                handleAction('deprecate', collection)
                            }
                        >
                            Deprecate
                        </MenuItem>
                    )}
                </DropdownKebab>
            </div>
        );
    }

    private renderAdditional(collection) {
        const items = [];

        items.push(
            <ListView.InfoItem key='repo-score'>
                <Score repo={collection} />
            </ListView.InfoItem>,
        );

        items.push(
            <ListView.InfoItem key='import-status'>
                <Link to={`/my-imports?namespace=${this.props.namespace.name}`}>
                    See Imports
                </Link>
            </ListView.InfoItem>,
        );

        if (collection.deprecated) {
            items.push(
                <ListView.InfoItem key='repo-deprecated'>
                    <span className='label label-danger'>Deprecated</span>
                </ListView.InfoItem>,
            );
        }

        return items;
    }
}
