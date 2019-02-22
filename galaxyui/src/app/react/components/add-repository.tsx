import * as React from 'react';

// Components
import { DropdownButton, MenuItem, Form } from 'react-bootstrap';
import {
    FormControl,
    ListView,
    ListViewItem,
    EmptyState,
    Button,
} from 'patternfly-react';
import { PageLoading } from './page-loading';

//Types
import { Namespace } from '../../resources/namespaces/namespace';
import { ProviderNamespace } from '../shared-types/add-repository';

interface IProps {
    namespace: Namespace;
    selectedPNS: ProviderNamespace;
    providerNamespaces: ProviderNamespace[];
    emptyStateIcon: string;
    emptyStateText: string;
    isSaving: boolean;

    //Callbacks
    close: () => void;
    selectProviderNamespace: (ns: ProviderNamespace) => void;
    filterRepos: (filter: string) => void;
    updateSelected: (repo: string) => void;
    saveRepos: () => void;
}

export class AddRepositoryModal extends React.Component<IProps> {
    render() {
        return (
            <div className='add-repository-modal-wrapper'>
                {this.renderHeader()}
                {this.renderBody()}
                {this.renderFooter()}
                <PageLoading loading={this.props.isSaving} />
            </div>
        );
    }

    private renderFooter() {
        return (
            <div className='modal-footer'>
                <Button
                    bsStyle='primary'
                    onClick={() => this.props.saveRepos()}
                >
                    OK
                </Button>
                <Button bsStyle='warning' onClick={this.props.close}>
                    Cancel
                </Button>
            </div>
        );
    }

    private renderBody() {
        return (
            <div className='modal-body add-repo-modal-body'>
                <div className='container-fluid'>
                    <div className='toolbar-pf add-repo-modal-toolbar'>
                        {this.renderToolbar()}
                        {this.renderRepos()}
                    </div>
                </div>
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

    private renderHeader() {
        return (
            <div className='modal-header'>
                <h4 className='modal-title pull-left'>
                    Add Repositories to {this.props.namespace.name}
                </h4>
                <button
                    type='button'
                    className='close pull-right'
                    aria-label='Close'
                    onClick={this.props.close}
                >
                    <span aria-hidden='true'>&times;</span>
                </button>
            </div>
        );
    }
}
