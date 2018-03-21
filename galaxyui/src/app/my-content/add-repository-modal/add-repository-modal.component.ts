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
    //private filterValue = new Subject<string>();

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
        this.saveInProgress = true;
        let saveRequests: Observable<Repository>[] = [];
        this.selectedPNS.repoSources
            .filter((repoSource) => repoSource.isSelected)
            .forEach(repoSource => {
                let newRepo = new Repository();
                newRepo.name = repoSource.name;
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
                let repoImport: RepositoryImport = new RepositoryImport();
                repoImport.github_user = repository.summary_fields.provider_namespace.name;
                repoImport.github_repo = repository.original_name;
                this.repositoryImportService
                    .save(repoImport)
                    .subscribe(_ => {
                        console.log();
                    });
            });
        });
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
