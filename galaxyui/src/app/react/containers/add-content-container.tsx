import * as React from 'react';

import { cloneDeep } from 'lodash';
import { BsModalRef } from 'ngx-bootstrap';

import { forkJoin, Observable } from 'rxjs';

import { Namespace } from '../../resources/namespaces/namespace';
import { ProviderSourceService } from '../../resources/provider-namespaces/provider-source.service';
import { Repository } from '../../resources/repositories/repository';
import { RepositoryService } from '../../resources/repositories/repository.service';
import { CollectionUpload } from '../../resources/collections/collection';
import { CollectionUploadService } from '../../resources/collections/collection.service';

import { Injector } from '@angular/core';
import { HttpEventType, HttpResponse } from '@angular/common/http';

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
    // GitHub Import
    selectedPNS: ProviderNamespace;
    emptyStateIcon: string;
    emptyStateText: string;

    // Shared
    isSaving: boolean;
    displayedComponent: View;
    modalTitle: string;
    buttonsDisplayed: ButtonConfig;

    // Collection Import
    collectionFile: File;
    fileErrors: string;
    uploadProgress: number;
    uploadStatus: string;
}

const AcceptedFileTypes = ['application/x-gzip', 'application/gzip'];

export class AddContentModalContainer extends React.Component<IProps, IState> {
    // Used to track which component is being loaded
    componentName = 'AddRepositoryModalComponent';

    providerNamespaces: ProviderNamespace[] = [];
    filterValue = '';

    // Services
    bsModalRef: BsModalRef;
    repositoryService: RepositoryService;
    providerSourceService: ProviderSourceService;
    collectionService: CollectionUploadService;

    uploadSubscription: any;

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
        this.collectionService = this.props.injector.get(
            CollectionUploadService,
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
            uploadProgress: 0,
            uploadStatus: 'waiting',
        };
    }

    componentDidMount() {
        this.setLoadingStateConfig();
    }

    componentWillUnmount() {
        // Cancel any uploads in progress if the modal is closed.
        if (this.uploadSubscription) {
            this.uploadSubscription.unsubscribe();
        }
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
                disableOkay={
                    this.state.fileErrors !== '' ||
                    this.state.uploadStatus !== 'waiting'
                }
            >
                {this.loadModalBody()}
            </ImportModal>
        );
    }

    // General Methods
    private loadModalBody() {
        // Loads view that the user selects
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
                        uploadProgress={this.state.uploadProgress}
                        uploadStatus={this.state.uploadStatus}
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

    private setDisplayedContent(view: View) {
        // Updates the selected view with the component state that is required
        // for that view.
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
                    uploadStatus: 'waiting',
                    uploadProgress: 0,
                });
                break;
            case View.PickImport:
                this.setState({
                    modalTitle: 'Add Content',
                    buttonsDisplayed: {
                        back: false,
                        okay: { enabled: false, text: 'OK' },
                        cancel: true,
                    },
                    displayedComponent: View.PickImport,
                });
                break;
        }
    }

    private save() {
        // Saves the selected repos or collection.
        if (this.state.displayedComponent === View.RepoImport) {
            this.saveRepos();
        } else if (this.state.displayedComponent === View.CollectionImport) {
            this.saveCollection();
        }
    }

    // Collection Methods
    private handleFileUpload(files) {
        // Selects the artificat that will be uploaded and performs some basic
        // preliminary checks on it.
        const newCollection = files[0];

        if (files.length > 1) {
            this.setState({
                fileErrors: 'Please select no more than one file.',
            });
        } else if (!AcceptedFileTypes.includes(newCollection.type)) {
            this.setState({
                fileErrors: 'Invalid file format.',
                collectionFile: newCollection,
                uploadProgress: 0,
            });
        } else {
            this.setState({
                fileErrors: '',
                collectionFile: newCollection,
                uploadProgress: 0,
            });
        }
    }

    private saveCollection() {
        // Uploads the selected collection to the galaxy API
        this.setState({ uploadStatus: 'uploading' });
        const artifact = {
            file: this.state.collectionFile,
            sha256: '',
        } as CollectionUpload;

        this.uploadSubscription = this.collectionService
            .upload(artifact)
            .subscribe(
                response => {
                    if (response['type'] === HttpEventType.UploadProgress) {
                        // Updates progress bar
                        this.setState({
                            uploadProgress: response.loaded / response.total,
                        });
                    } else if (response instanceof HttpResponse) {
                        // Upload succeeds
                        this.props.updateAdded(true);
                        this.bsModalRef.hide();
                    }
                },
                error => {
                    // Upload fails
                    this.props.updateAdded(false);
                    let errorMessage = '';
                    if (typeof error.error === 'object') {
                        for (const field of Object.keys(error.error)) {
                            errorMessage += error.error[field] + ' ';
                        }
                    } else {
                        errorMessage = error.error;
                    }

                    this.setState({
                        uploadStatus: 'waiting',
                        fileErrors: errorMessage,
                    });
                },
            );
    }

    // Repository import methods
    private selectProviderNamespace(pns: ProviderNamespace) {
        // Updates the provider namespace and pulls a list of repos from it
        this.setState({ selectedPNS: pns }, () => this.getRepoSources());
    }

    private filterFromView(filterValue) {
        // Updates the list of filtered repos on the selected provider namespace
        const pns = cloneDeep(this.state.selectedPNS);
        this.setState({ selectedPNS: this.filterRepos(filterValue, pns) });
    }

    private filterRepos(filterValue: string, oldPNS) {
        // Copies the selected provider namespace out of state and returns an
        // updated version with a filtered list of repos.
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
        // Handles checking and unchecking repositories in the list of repos
        const pns = cloneDeep(this.state.selectedPNS);

        const i = pns.repoSources.findIndex(el => el.name === repoName);
        pns.repoSources[i].isSelected = !pns.repoSources[i].isSelected;

        this.setState({ selectedPNS: pns });
    }

    private saveRepos() {
        // Submits the list of checked repos to the API so that they can be
        // imported.
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
        // Sets empty state for repository list
        this.setState({
            emptyStateIcon: 'pficon pficon-warning-triangle-o',
            emptyStateText: 'No matching repositories found!',
        });
    }

    private setLoadingStateConfig() {
        // Sets loading state for repository list
        this.setState({
            emptyStateIcon: 'spinner fa-pulse',
            emptyStateText: 'Loading repositories...',
        });
    }

    private getRepoSources() {
        // Loads the list of repositories for a given provider namespace from
        // the API.
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
