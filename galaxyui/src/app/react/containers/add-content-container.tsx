import * as React from 'react';

import { cloneDeep } from 'lodash';
import { BsModalRef } from 'ngx-bootstrap';

import { forkJoin, Observable } from 'rxjs';

import { Namespace } from '../../resources/namespaces/namespace';
import { ProviderSourceService } from '../../resources/provider-namespaces/provider-source.service';
import { Repository } from '../../resources/repositories/repository';
import { RepositoryService } from '../../resources/repositories/repository.service';

import { Injector } from '@angular/core';

import { RepoImportView } from '../components/import-modal/repo-import-view';
import { ImportModal } from '../components/import-modal/import-modal';
import { PickImportType } from '../components/import-modal/pick-import-type';
import { UploadCollection } from '../components/import-modal/upload-collection';

import {
    ProviderNamespace,
    RepositorySource,
    View,
    ButtonConfig,
} from '../shared-types/add-repository';

interface IProps {
    injector: Injector;
    namespace: Namespace;
    updateAdded: (added: boolean) => void;
}

interface IState {
    selectedPNS: ProviderNamespace;
    emptyStateIcon: string;
    emptyStateText: string;
    isSaving: boolean;
    displayedComponent: View;
    modalTitle: string;
    buttonsDisplayed: ButtonConfig;
    collectionFile: any;
    fileErrors: string;
}

const AcceptedFileTypes = ['application/x-tar'];

export class AddContentModalContainer extends React.Component<IProps, IState> {
    // Used to track which component is being loaded
    componentName = 'AddRepositoryModalComponent';

    providerNamespaces: ProviderNamespace[] = [];
    filterValue = '';

    // Services
    bsModalRef: BsModalRef;
    repositoryService: RepositoryService;
    providerSourceService: ProviderSourceService;

    constructor(props) {
        super(props);
        this.providerNamespaces = [];
        this.props.namespace.summary_fields.provider_namespaces.forEach(pns => {
            this.providerNamespaces.push(cloneDeep(pns));
        });

        let selectedPNS;

        if (this.providerNamespaces.length > 0) {
            selectedPNS = this.providerNamespaces[0];
        }

        this.bsModalRef = this.props.injector.get(BsModalRef);
        this.repositoryService = this.props.injector.get(RepositoryService);
        this.providerSourceService = this.props.injector.get(
            ProviderSourceService,
        );

        this.state = {
            selectedPNS: selectedPNS,
            emptyStateIcon: 'spinner fa-pulse',
            emptyStateText: 'Loading repositories...',
            isSaving: false,
            displayedComponent: View.PickImport,
            modalTitle: 'Add Content',
            buttonsDisplayed: {
                back: false,
                okay: { enabled: false, text: 'OK' },
                cancel: true,
            },
            collectionFile: null,
            fileErrors: '',
        };
    }

    componentDidMount() {
        this.setLoadingStateConfig();
    }

    render() {
        return (
            <ImportModal
                title={this.state.modalTitle}
                isSaving={this.state.isSaving}
                buttonsDisplayed={this.state.buttonsDisplayed}
                save={() => this.save()}
                close={() => this.bsModalRef.hide()}
                setDisplayedContent={x => this.setDisplayedContent(x)}
            >
                {this.loadModalBody()}
            </ImportModal>
        );
    }

    private loadModalBody() {
        switch (this.state.displayedComponent) {
            case View.RepoImport:
                return (
                    <RepoImportView
                        selectedPNS={this.state.selectedPNS}
                        providerNamespaces={this.providerNamespaces}
                        emptyStateIcon={this.state.emptyStateIcon}
                        emptyStateText={this.state.emptyStateText}
                        selectProviderNamespace={x =>
                            this.selectProviderNamespace(x)
                        }
                        filterRepos={x => this.filterFromView(x)}
                        updateSelected={x => this.handleSelectionChange(x)}
                    />
                );

            case View.CollectionImport:
                return (
                    <UploadCollection
                        handeFileUpload={x => this.handleFileUpload(x)}
                        file={this.state.collectionFile}
                        errors={this.state.fileErrors}
                    />
                );

            case View.PickImport:
                return (
                    <PickImportType
                        setView={x => this.setDisplayedContent(x)}
                    />
                );
        }
    }

    private handleFileUpload(files) {
        const newCollection = files[0];

        if (files.length > 1) {
            this.setState({
                fileErrors: 'Please select no more than one file.',
            });
        } else if (!AcceptedFileTypes.includes(newCollection.type)) {
            this.setState({
                fileErrors: 'Invalid file format.',
                collectionFile: newCollection,
            });
        } else {
            this.setState({
                fileErrors: '',
                collectionFile: newCollection,
            });
        }
    }

    private setDisplayedContent(view: View) {
        switch (view) {
            case View.RepoImport:
                this.setState(
                    {
                        modalTitle:
                            'Add repositories to ' + this.props.namespace.name,
                        buttonsDisplayed: {
                            back: true,
                            okay: { enabled: true, text: 'OK' },
                            cancel: true,
                        },
                        displayedComponent: View.RepoImport,
                    },
                    () => this.getRepoSources(),
                );
                break;
            case View.CollectionImport:
                this.setState({
                    modalTitle: 'Upload a New Collection',
                    buttonsDisplayed: {
                        back: true,
                        okay: { enabled: true, text: 'Upload' },
                        cancel: true,
                    },
                    displayedComponent: View.CollectionImport,
                });
                break;
            case View.PickImport:
                this.setState({
                    modalTitle: 'Add Content',
                    buttonsDisplayed: {
                        back: false,
                        okay: { enabled: false, text: 'OK' },
                        cancel: false,
                    },
                    displayedComponent: View.PickImport,
                });
                break;
        }
    }

    private selectProviderNamespace(pns: ProviderNamespace) {
        this.setState({ selectedPNS: pns }, () => this.getRepoSources());
    }

    private filterFromView(filterValue) {
        const pns = cloneDeep(this.state.selectedPNS);
        this.setState({ selectedPNS: this.filterRepos(filterValue, pns) });
    }

    private filterRepos(filterValue: string, oldPNS) {
        const pns = cloneDeep(oldPNS);
        if (filterValue) {
            this.filterValue = filterValue;
            pns.filteredSources = pns.repoSources.filter(repo =>
                repo.name.toLowerCase().match(filterValue.toLowerCase()),
            );
        } else {
            this.filterValue = '';
            pns.filteredSources = pns.repoSources;
        }

        return pns;
    }

    private handleSelectionChange(repoName: string) {
        const pns = cloneDeep(this.state.selectedPNS);

        const i = pns.repoSources.findIndex(el => el.name === repoName);
        pns.repoSources[i].isSelected = !pns.repoSources[i].isSelected;

        this.setState({ selectedPNS: pns });
    }

    private save() {
        if (this.state.displayedComponent === View.RepoImport) {
            this.saveRepos();
        } else if (this.state.displayedComponent === View.CollectionImport) {
            this.saveCollection();
        }
    }

    private saveCollection() {
        console.log(this.state.collectionFile);
        this.bsModalRef.hide();
    }

    private saveRepos() {
        this.props.updateAdded(true);
        this.setState({ isSaving: true });
        const saveRequests: Observable<Repository>[] = [];
        const selected: RepositorySource[] = this.state.selectedPNS.repoSources.filter(
            repoSource => repoSource.isSelected,
        );

        if (!selected.length) {
            // nothing was selected
            this.props.updateAdded(false);
            this.bsModalRef.hide();
            return;
        }

        selected.forEach(repoSource => {
            const newRepo = new Repository();
            newRepo.name = repoSource.name;
            newRepo.original_name = repoSource.name;
            newRepo.description = repoSource.description
                ? repoSource.description
                : repoSource.name;
            newRepo.provider_namespace = this.state.selectedPNS.id;
            newRepo.is_enabled = true;
            saveRequests.push(this.repositoryService.save(newRepo));
        });

        forkJoin(saveRequests).subscribe((results: Repository[]) => {
            this.bsModalRef.hide();
        });
    }

    private setEmptyStateConfig() {
        this.setState({
            emptyStateIcon: 'pficon pficon-warning-triangle-o',
            emptyStateText: 'No matching repositories found!',
        });
    }

    private setLoadingStateConfig() {
        this.setState({
            emptyStateIcon: 'spinner fa-pulse',
            emptyStateText: 'Loading repositories...',
        });
    }

    private getRepoSources() {
        if (
            !this.state.selectedPNS['repoSources'] ||
            !this.state.selectedPNS.repoSources.length
        ) {
            let pns = cloneDeep(this.state.selectedPNS);
            this.setLoadingStateConfig();
            pns.repoSources = [];
            pns.filteredSources = [];
            this.providerSourceService
                .getRepoSources({
                    providerName: pns.provider_name,
                    name: pns.name,
                })
                .subscribe(repoSources => {
                    repoSources.forEach(repoSource => {
                        if (!repoSource.summary_fields.repository) {
                            repoSource['isSelected'] = false;
                            pns.repoSources.push(
                                repoSource as RepositorySource,
                            );
                        }
                    });
                    pns = this.filterRepos(this.filterValue, pns);
                    this.setEmptyStateConfig();

                    this.setState({ selectedPNS: pns });
                });
        } else {
            this.setState({
                selectedPNS: this.filterRepos(
                    this.filterValue,
                    this.state.selectedPNS,
                ),
            });
            this.setEmptyStateConfig();
        }
    }
}
