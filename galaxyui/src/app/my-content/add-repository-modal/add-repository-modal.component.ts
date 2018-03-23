import { Component, OnInit }       from '@angular/core';
import { BsModalRef }              from 'ngx-bootstrap';
import { Namespace }               from '../../resources/namespaces/namespace';
import { ProviderNamespace }       from '../../resources/provider-namespaces/provider-namespace';
import { cloneDeep }               from 'lodash';
import { ProviderSourceService }   from '../../resources/provider-namespaces/provider-source.service';
import { Subject }                 from 'rxjs';
import { forkJoin }                from 'rxjs/observable/forkJoin';
import { Observable }              from 'rxjs/Observable';
import { RepositoryService }       from '../../resources/respositories/repository.service';
import { Repository }              from '../../resources/respositories/repository';
import { RepositoryImport }        from '../../resources/repository-imports/repository-import';
import { RepositoryImportService } from '../../resources/repository-imports/repository-import.service';


@Component({
    selector: 'add-repository-modal',
    templateUrl: './add-repository-modal.component.html',
    styleUrls: ['./add-repository-modal.component.less']
})
export class AddRepositoryModalComponent implements OnInit {
    namespace: Namespace;
    selectedPNS: any;
    providerNamespaces: any[] = [];
    originalRepos: any[] = [];
    displayedRepos: any[] = [];
    saveInProgress: boolean;
    repositoriesAdded: boolean = false;

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
            this.selectedPNS = this.providerNamespaces[0]
        }
        this.getRepoSources();
    }

    selectProviderNamespace(pns:ProviderNamespace) {
        this.selectedPNS = pns;
    }

    filterRepos(filterValue:string) {
        //this.filterValue.next(filterValue);
        this.providerNamespaces.forEach(pns => {
            if (filterValue) {
                pns.displaySources = [];
                pns.repoSources.forEach(repo => {
                    if (repo.name.toLowerCase().match(filterValue.toLowerCase()) !== null) {
                        pns.displaySources.push(JSON.parse(JSON.stringify(repo)));
                    }
                });
            } else {
                pns.displaySources = JSON.parse(JSON.stringify(pns.repoSources));
            }
        });
    }

    selectRepo(repo: any) {
        repo.isSelected = !repo.isSelected;
        this.selectedPNS.repoSources.forEach(srcRepo => {
            if (srcRepo.name == repo.name) {
                srcRepo.isSelected = repo.isSelected;
            }
        });
    }

    saveRepos() {
        this.repositoriesAdded = true;
        this.saveInProgress = true;
        let saveRequests: Observable<Repository>[] = [];
        this.selectedPNS.repoSources
            .filter((repoSource) => repoSource.isSelected)
            .forEach(repoSource => {
                let newRepo = new Repository();
                newRepo.name = this.getRepoName(repoSource.name);
                newRepo.original_name = repoSource.name;
                newRepo.description = repoSource.description ? repoSource.description : repoSource.name;
                newRepo.provider_namespace = this.selectedPNS.id;
                newRepo.is_enabled = true;
                saveRequests.push(this.repositoryService.save(newRepo));
                //TODO catch errors from the save and ignore them or else forkjoin will fail.
            });

        forkJoin(saveRequests).subscribe((results: Repository[]) => {
            this.saveInProgress = false;
            this.bsModalRef.hide();
            results.forEach((repository: Repository) => {
                this.repositoryImportService
                    .save({'repository_id': repository.id})
                    .subscribe(_ => {
                        console.log(`Started import for ${repository.name}`);
                    });
            });
        });
    }

    private getRepoName(original_name: string): string {
        // This is the logic from Galaxy < 3.0 for setting the repoo name
        let new_name: string;
        if (original_name != 'ansible') {
            original_name.replace(/^(ansible[-_+.]*)*(role[-_+.]*)*/g, function(match, p1, p2, offset, str): string {
                let result = str;
                if (p1) {
                    result = result.replace(new RegExp(p1, 'g'), '');
                }
                if (p2) {
                    result = result.replace(new RegExp(p2, 'g'), '');
                }
                result = result.replace(/^-/, '');
                new_name = result;
                return '';
            });
        }
        return new_name || original_name;
    }

    private getRepoSources() {
        this.providerNamespaces.forEach(pns => {
            pns.loading = true;
            pns.repoSources = [];
            pns.displaySources = [];
            this.providerSourceService.getRepoSources({
                providerName: pns.provider_name,
                name: pns.name
            }).subscribe(repoSources => {
                repoSources.forEach(repoSource => {
                    if (!repoSource.summary_fields.repository) {
                        pns.repoSources.push(repoSource);
                    }
                });
                pns.displaySources = JSON.parse(JSON.stringify(pns.repoSources));
                pns.loading = false;
            });
        });
    }
}
