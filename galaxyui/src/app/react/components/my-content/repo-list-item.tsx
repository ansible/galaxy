import * as React from 'react';

import {
    ListView,
    ListViewItem,
    OverlayTrigger,
    Tooltip,
    Button,
    DropdownKebab,
    MenuItem,
} from 'patternfly-react';
import { Repository } from '../../../resources/repositories/repository';
import { Link } from '../../lib/link';
import { Namespace } from '../../../resources/namespaces/namespace';
import { Score } from '../score';

interface IProps {
    repo: Repository;
    namespace: Namespace;
    handleAction: (event, repo: Repository) => void;
}

export class RepoListItem extends React.Component<IProps, {}> {
    render() {
        const { repo } = this.props;
        return (
            <ListViewItem
                leftContent={
                    repo.summary_fields.loading ? (
                        <div className='spinner spin-wrapper' />
                    ) : (
                        <i className={repo['iconClass']} />
                    )
                }
                key={repo.name}
                heading={<Link to={repo['detail_url']}>{repo.name}</Link>}
                description={repo.description}
                additionalInfo={this.renderAdditional(repo)}
                actions={this.renderActions(repo)}
            />
        );
    }

    private renderActions(repo) {
        const { handleAction } = this.props;

        let importing = false;
        if (
            repo['latest_import'] &&
            (repo['latest_import']['state'] === 'PENDING' ||
                repo['latest_import']['state'] === 'RUNNING')
        ) {
            importing = true;
        }

        if (repo['summary_fields']['loading']) {
            importing = true;
        }

        return (
            <div>
                <Button
                    disabled={importing}
                    onClick={() => handleAction('import', repo)}
                >
                    <i className='fa fa-upload' /> Import
                </Button>
                <DropdownKebab id='repo-actions' pullRight>
                    <MenuItem
                        disabled={importing}
                        onClick={() => handleAction('delete', repo)}
                    >
                        Delete
                    </MenuItem>
                    {repo.deprecated ? (
                        <MenuItem
                            disabled={importing}
                            onClick={() => handleAction('undeprecate', repo)}
                        >
                            Undeprecate
                        </MenuItem>
                    ) : (
                        <MenuItem
                            disabled={importing}
                            onClick={() => handleAction('deprecate', repo)}
                        >
                            Deprecate
                        </MenuItem>
                    )}
                </DropdownKebab>
            </div>
        );
    }

    private renderAdditional(repo) {
        const items = [];

        const importLink = `/my-imports/${this.props.namespace.id}?type=repository&name=${repo.name}`;

        let importElement = <span className='text'>Status Unknown</span>;

        if (
            repo['latest_import'] &&
            (repo['latest_import']['state'] === 'PENDING' ||
                repo['latest_import']['state'] === 'RUNNING')
        ) {
            importElement = (
                <Link to={importLink} className='running'>
                    <i className='fa fa-spin fa-spinner patternfly-list-additional-override' />{' '}
                    <span className='text'>
                        Running {repo['latest_import']['as_of_dt']}
                    </span>
                </Link>
            );
        }

        if (
            repo['latest_import'] &&
            repo['latest_import']['state'] === 'SUCCESS'
        ) {
            importElement = (
                <Link to={importLink} className='succeeded'>
                    <i className='fa fa-circle patternfly-list-additional-override' />{' '}
                    <span className='text'>
                        Succeeded {repo['latest_import']['as_of_dt']}
                    </span>
                </Link>
            );
        }

        if (
            repo['latest_import'] &&
            repo['latest_import']['state'] === 'FAILED'
        ) {
            importElement = (
                <Link to={importLink} className='failed'>
                    <i className='fa fa-circle patternfly-list-additional-override' />{' '}
                    <span className='text'>
                        Failed {repo['latest_import']['as_of_dt']}
                    </span>
                </Link>
            );
        }

        items.push(
            <ListView.InfoItem key='repo-score'>
                <Score repo={repo} />
            </ListView.InfoItem>,
        );

        items.push(
            <ListView.InfoItem key='import-status'>
                <OverlayTrigger
                    overlay={
                        <Tooltip id='view-import'>View Import Log</Tooltip>
                    }
                    placement='top'
                    trigger={['hover', 'focus']}
                    rootClose={false}
                >
                    {importElement}
                </OverlayTrigger>
            </ListView.InfoItem>,
        );

        if (repo.deprecated) {
            items.push(
                <ListView.InfoItem key='repo-deprecated'>
                    <span className='label label-danger'>Deprecated</span>
                </ListView.InfoItem>,
            );
        }

        return items;
    }
}
