import {
    Component,
    OnInit
} from '@angular/core';

import { EmptyStateConfig }        from 'patternfly-ng/empty-state/empty-state-config';
import { ListEvent }               from 'patternfly-ng/list/list-event';
import { ListConfig }              from 'patternfly-ng/list/basic-list/list-config';

import { BsModalRef }              from 'ngx-bootstrap';
import { cloneDeep }               from 'lodash';

import { Subject }                 from 'rxjs';
import { forkJoin }                from 'rxjs/observable/forkJoin';
import { Observable }              from 'rxjs/Observable';

import { Namespace }               from '../../resources/namespaces/namespace';
import { ProviderSourceService }   from '../../resources/provider-namespaces/provider-source.service';
import { RepositoryService }       from '../../resources/repositories/repository.service';
import { Repository }              from '../../resources/repositories/repository';
import { RepositoryImport }        from '../../resources/repository-imports/repository-import';
import { RepositoryImportService } from '../../resources/repository-imports/repository-import.service';

class RepositorySource {
    name: string;
    description: string;
    stargazers_count: number;
    watchers_count: number;
    forks_count: number;
    open_issues_count: number;
    default_branch: string;
    related: any;
    summary_fields: any;
    isSelected: boolean;
}

class ProviderNamespace {
    id: number;
    name: string;
    description: string;
    display_name: string;
    avatar_url: string;
    location: string;
    company: string;
    email: string;
    html_url: string;
    followers: number;
    provider: number;
    provider_name: string;
    related: object;
    summary_fields: any;
    repoSources: RepositorySource[];
    filteredSources: RepositorySource[];
}


@Component({
    selector: 'add-repository-modal',
    templateUrl: './add-repository-modal.component.html',
    styleUrls: ['./add-repository-modal.component.less']
})
export class AddRepositoryModalComponent implements OnInit {

    emptyStateConfig: EmptyStateConfig = {} as EmptyStateConfig;
    namespace: Namespace;
    selectedPNS: ProviderNamespace;
    providerNamespaces: ProviderNamespace[] = [];
    originalRepos: any[] = [];
    displayedRepos: any[] = [];
    saveInProgress: boolean;
    repositoriesAdded = false;
    listConfig: ListConfig;
    filterValue = '';

    constructor(public bsModalRef: BsModalRef,
                private repositoryService: RepositoryService,
                private repositoryImportService: RepositoryImportService,
                private providerSourceService: ProviderSourceService) {
    }

    ngOnInit() {
        this.providerNamespaces = [];
        this.namespace.summary_fields.provider_namespaces.forEach(pns => {
            this.providerNamespaces.push(cloneDeep(pns));
        });
        if (this.providerNamespaces.length > 0) {
            this.selectedPNS = this.providerNamespaces[0];
        }

        this.setLoadingStateConfig();

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: false,
            selectionMatchProp: 'name',
            showCheckbox: true,
            showRadioButton: false,
            useExpandItems: false,
            emptyStateConfig: this.emptyStateConfig
        } as ListConfig;

        this.getRepoSources();
    }

    selectProviderNamespace(pns: ProviderNamespace) {
        this.selectedPNS = pns;
        this.getRepoSources();
    }

    filterRepos(filterValue: string) {
        if (filterValue) {
            this.filterValue = filterValue;
            this.selectedPNS.filteredSources = this.selectedPNS.repoSources.filter(
                repo => repo.name.toLowerCase().match(filterValue.toLowerCase()));
        } else {
            this.filterValue = '';
            this.selectedPNS.filteredSources = this.selectedPNS.repoSources;
        }
    }

    handleSelectionChange($event: ListEvent) {
        this.selectedPNS.repoSources.forEach((repo: RepositorySource) => {
            repo.isSelected = false;
            $event.selectedItems.forEach((selectedRepo: RepositorySource) => {
                if (selectedRepo.name === repo.name) {
                    repo.isSelected = true;
                }
            });
        });
        this.selectedPNS.filteredSources.forEach((repo: RepositorySource) => {
            repo.isSelected = false;
            $event.selectedItems.forEach((selectedRepo: RepositorySource) => {
                if (selectedRepo.name === repo.name) {
                    repo.isSelected = true;
                }
            });
        });
    }

    saveRepos() {
        this.repositoriesAdded = true;
        this.saveInProgress = true;
        const saveRequests: Observable<Repository>[] = [];
        this.selectedPNS.repoSources
            .filter((repoSource) => repoSource.isSelected)
            .forEach(repoSource => {
                const newRepo = new Repository();
                newRepo.name = repoSource.name;
                newRepo.original_name = repoSource.name;
                newRepo.description = repoSource.description ? repoSource.description : repoSource.name;
                newRepo.provider_namespace = this.selectedPNS.id;
                newRepo.is_enabled = true;
                saveRequests.push(this.repositoryService.save(newRepo));
            });

        forkJoin(saveRequests).subscribe((results: Repository[]) => {
            this.saveInProgress = false;
            this.bsModalRef.hide();
        });
    }

    // private

    private setEmptyStateConfig() {
        this.emptyStateConfig.iconStyleClass = 'pficon-warning-triangle-o';
        this.emptyStateConfig.title = 'No matching repositories found!';
        this.emptyStateConfig.info = '';
    }

    private setLoadingStateConfig() {
        this.emptyStateConfig.iconStyleClass = 'fa fa-spinner fa-pulse';
        this.emptyStateConfig.title = 'Loading repositories...';
        this.emptyStateConfig.info = '';
    }

    private getRepoSources() {
        if (!this.selectedPNS['repoSources'] || !this.selectedPNS.repoSources.length) {
            this.setLoadingStateConfig();
            this.selectedPNS.repoSources = [];
            this.selectedPNS.filteredSources = [];
            this.providerSourceService.getRepoSources({
                providerName: this.selectedPNS.provider_name,
                name: this.selectedPNS.name
            }).subscribe(repoSources => {
                repoSources.forEach(repoSource => {
                    if (!repoSource.summary_fields.repository) {
                        this.selectedPNS.repoSources.push(repoSource as RepositorySource);
                    }
                });
                this.filterRepos(this.filterValue);
                this.setEmptyStateConfig();
            });
        } else {
            this.filterRepos(this.filterValue);
            this.setEmptyStateConfig();
        }
    }
}
