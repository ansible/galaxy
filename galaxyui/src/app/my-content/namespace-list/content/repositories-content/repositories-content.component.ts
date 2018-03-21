import {
    Component,
    OnInit,
    OnDestroy,
    TemplateRef,
    ViewEncapsulation,
    Input,
} from '@angular/core';

import { flatten }           from 'lodash';
import { Action }            from 'patternfly-ng/action/action';
import { ActionConfig }      from 'patternfly-ng/action/action-config';
import { EmptyStateConfig }  from 'patternfly-ng/empty-state/empty-state-config';
import { ListEvent }         from 'patternfly-ng/list/list-event';
import { ListConfig }        from 'patternfly-ng/list/basic-list/list-config';

import { Namespace }               from "../../../../resources/namespaces/namespace";
import { Repository }              from "../../../../resources/respositories/repository";
import { RepositoryService }       from "../../../../resources/respositories/repository.service";
import { ProviderNamespace }       from "../../../../resources/provider-namespaces/provider-namespace";
import { RepositoryImportService } from "../../../../resources/repository-imports/repository-import.service";
import { RepositoryImport }        from "../../../../resources/repository-imports/repository-import";

import { Observable }              from "rxjs/Observable";
import { forkJoin }                from 'rxjs/observable/forkJoin';

import * as moment                 from 'moment';


@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'repositories-content',
    templateUrl: './repositories-content.component.html',
    styleUrls: ['./repositories-content.component.less']
})
export class RepositoriesContentComponent implements OnInit, OnDestroy {
    @Input() namespace: Namespace;

    items: Repository[] = [new Repository()];   // init with one empty repo to preven EmptyState from flashing on the page
    emptyStateConfig: EmptyStateConfig;
    listConfig: ListConfig;
    selectType: string = 'checkbox';
    loading: boolean = false;
    polling = null;

    constructor(private repositoryService: RepositoryService,
                private repositoryImportService: RepositoryImportService) {}

    ngOnInit(): void {
        this.emptyStateConfig = {
            actions: {
                primaryActions: [],
                moreActions: []
            } as ActionConfig,
            iconStyleClass: 'pficon-warning-triangle-o',
            title: 'No Repositories',
            info: "Add repositories by clicking the 'Add Content' button above.",
            helpLink: {}
        } as EmptyStateConfig;

        this.listConfig = {
            dblClick: false,
            emptyStateConfig: this.emptyStateConfig,
            multiSelect: false,
            selectItems: false,
            selectionMatchProp: 'name',
            showCheckbox: false,
            useExpandItems: false
        } as ListConfig;

        this.getRepositories();
    }

    ngDoCheck(): void {}

    ngOnDestroy(): void {
        if (this.polling)
            this.polling.unsubscribe();
    }

    getActionConfig(item: Repository,
                    actionButtonTemplate: TemplateRef<any>,
                    importButtonTemplate: TemplateRef<any>): ActionConfig {
        let actionConfig = {
            primaryActions: [{
                id: 'import',
                title: 'Import',
                tooltip: 'Import Repository',
                template: importButtonTemplate
            }],
            moreActions: [{
                id: 'delete',
                title: 'Delete',
                tooltip: 'Delete Repository'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: true
        } as ActionConfig;

        // Set button disabled
        if (item['latest_import'] && (item['latest_import']['state'] === 'PENDING' || item['latest_import']['state'] === 'RUNNING')) {
            actionConfig.primaryActions[0].disabled = true;
            actionConfig.moreActionsVisible = false;
        }
        return actionConfig;
    }

    // Actions

    handleAction($event: Action, item: any): void {
        if ($event.id === 'import' && item) {
            this.importRepository(item);
        }
        if ($event.id == 'delete' && item) {
            this.deleteRepository(item);
        }
    }

    // Private

    private getRepositories() {
        this.loading = true;
        let queries: Observable<Repository[]>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            queries.push(this.repositoryService.query({'provider_namespace__id': pns.id}));
        });

        forkJoin(queries).subscribe((results: Repository[][]) => {
            let repositories = flatten(results);
            repositories.forEach(item => {
                item['latest_import'] = {};
                if (item.summary_fields.latest_import) {
                    item['latest_import'] = item.summary_fields.latest_import;
                    item['latest_import']['as_of_dt'] =
                        item['latest_import']['finished'] ? moment(item['latest_import']['finished']).fromNow() : moment(item['latest_import']['modified']).fromNow();
                }
            });
            
            this.items = JSON.parse(JSON.stringify(repositories));
            this.loading = false;

            if (this.items.length) {
                // Every 5 seconds, refresh the respository data
                this.polling = Observable.interval(5000)
                    .subscribe(_ => {
                        this.refreshRepositories();
                    });
            }
        });
    }

    private refreshRepositories() {
        this.loading = true;
        let queries: Observable<Repository[]>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            queries.push(this.repositoryService.query({ 'provider_namespace__id': pns.id }));
        });

        forkJoin(queries).subscribe((results: Repository[][]) => {
            let repositories = flatten(results);
            let match: boolean;
            repositories.forEach(repo => {
                match = false;
                this.items.forEach(item => {
                    // Update items in place, to avoid page bounce. Page bounce happens when all items are replaced. 
                    if (item.id == repo.id) {
                        match = true;
                        if (repo.summary_fields.latest_import) {
                            if (!item['latest_import']) {
                                item['latest_import'] = {};
                            }
                            item['latest_import'] = repo.summary_fields.latest_import;
                            item['latest_import']['as_of_dt'] =
                                item['latest_import']['finished'] ? moment(item['latest_import']['finished']).fromNow() : moment(item['latest_import']['modified']).fromNow();
                        } else {
                            item['latest_import'] = {};
                        }
                    }
                });
                if (!match) {
                    // repository doesn't exist, so add it
                    repo['latest_import'] = {};
                    if (repo.summary_fields.latest_import) {
                        repo['latest_import'] = repo.summary_fields.latest_import;
                        repo['latest_import']['as_of_dt'] =
                            repo['latest_import']['finished'] ? moment(repo['latest_import']['finished']).fromNow() : moment(repo['latest_import']['modified']).fromNow();
                    }
                    this.items.push(repo);
                }
            });
            this.loading = false;
        });
    }

    private importRepository(repository: Repository) {
        // Start an import
        let repoImport: RepositoryImport = new RepositoryImport();
        repoImport.github_user = repository.github_user;
        repoImport.github_repo = repository.github_repo;
        repository['latest_import']['state'] = 'PENDING';
        repository['latest_import']['as_of_dt'] = '';
        this.repositoryImportService.save(repoImport)
            .subscribe(
                response => {
                    console.log(`Fetched repoostiroy ${response.id}`);
                }
            );
    }

    private deleteRepository(repository: Repository) {
        this.loading = true;
        this.repositoryService.destroy(repository).subscribe( _ =>{
            this.items.forEach((item: Repository, idx: number) => {
                if (item.id == repository.id) {
                    this.items.splice(idx, 1);
                    this.loading = false;
                }
            });
        });
    }
}
