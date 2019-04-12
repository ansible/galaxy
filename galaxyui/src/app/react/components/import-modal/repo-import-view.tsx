import * as React from 'react';

// Components
import {
    DropdownButton,
    MenuItem,
    Form,
    FormControl,
    ListView,
    ListViewItem,
    EmptyState,
} from 'patternfly-react';

// Types
import { ProviderNamespace } from '../../shared-types/add-repository';

interface IProps {
    selectedPNS: ProviderNamespace;
    providerNamespaces: ProviderNamespace[];
    emptyStateIcon: string;
    emptyStateText: string;
    //
    // //Callbacks
    selectProviderNamespace: (ns: ProviderNamespace) => void;
    filterRepos: (filter: string) => void;
    updateSelected: (repo: string) => void;
}

export class RepoImportView extends React.Component<IProps> {
    render() {
        return (
            <div className='toolbar-pf add-repo-modal-toolbar'>
                {this.renderToolbar()}
                {this.renderRepos()}
            </div>
        );
    }

    private renderRepos() {
        if (
            !this.props.selectedPNS.filteredSources ||
            this.props.selectedPNS.filteredSources.length === 0
        ) {
            return (
                <div className='add-repo-modal-list'>
                    <EmptyState className='empty-state'>
                        <EmptyState.Icon
                            type={'fa'}
                            name={this.props.emptyStateIcon}
                        />
                        <EmptyState.Title>
                            {this.props.emptyStateText}
                        </EmptyState.Title>
                    </EmptyState>
                </div>
            );
        }

        return (
            <ListView className='add-repo-modal-list'>
                {this.props.selectedPNS.filteredSources.map(item => {
                    return (
                        <ListViewItem
                            checkboxInput={
                                <input
                                    type='checkbox'
                                    value={item.name}
                                    checked={item.isSelected}
                                    onChange={x =>
                                        this.props.updateSelected(
                                            x.target.value,
                                        )
                                    }
                                />
                            }
                            key={item.name}
                            leftContent={<i className='pficon-repository' />}
                            heading={
                                <span>
                                    {this.props.selectedPNS.name}/{item.name}
                                </span>
                            }
                        />
                    );
                })}
            </ListView>
        );
    }

    private renderToolbar() {
        return (
            <div className='toolbar-pf'>
                <Form inline>
                    <DropdownButton
                        id={'dropdown-basic'}
                        title={
                            <span>
                                {this.getProviderIcon(this.props.selectedPNS)}{' '}
                                {this.props.selectedPNS.name}
                            </span>
                        }
                    >
                        <MenuItem key={0} disabled={true}>
                            <i>Select provider namespace...</i>
                        </MenuItem>
                        {this.props.providerNamespaces.map(item => {
                            return (
                                <MenuItem
                                    onSelect={
                                        this.props.selectProviderNamespace
                                    }
                                    key={item.id}
                                    eventKey={item}
                                >
                                    {this.getProviderIcon(item)} {item.name}
                                </MenuItem>
                            );
                        })}
                    </DropdownButton>

                    <FormControl
                        className='modal-filter'
                        type={'text'}
                        placeholder={'Filter by name...'}
                        onChange={e => this.props.filterRepos(e.target.value)}
                        onKeyPress={e => {
                            if (e.key === 'Enter') {
                                event.stopPropagation();
                                event.preventDefault();
                            }
                        }}
                    />
                </Form>
            </div>
        );
    }

    private getProviderIcon(pns) {
        if (pns.provider_name === 'github') {
            return <i className='fa fa-github' />;
        }
    }
}
