import * as React from 'react';
import { CollectionList } from '../../../resources/collections/collection';
import { Namespace } from '../../../resources/namespaces/namespace';
import { Link } from '../../lib/link';

import {
    ListView,
    ListViewItem,
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
                    <Link to={`/${namespace.name}/${collection.name}`}>
                        {collection.name}
                    </Link>
                }
                description={collection.latest_version.metadata.description}
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

        const scoreData = {
            community_score: collection.community_score,
            quality_score: collection.latest_version.quality_score,
            community_survey_count: collection.community_survey_count,
        };

        items.push(
            <ListView.InfoItem key='repo-score'>
                <Score repo={scoreData} />
            </ListView.InfoItem>,
        );

        items.push(
            <ListView.InfoItem key='import-status'>
                <Link
                    to={`/my-imports/${
                        this.props.namespace.id
                    }?type=collection&name=${this.props.collection.name}`}
                >
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
