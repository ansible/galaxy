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

import {
    BsModalService,
    BsModalRef 
} from 'ngx-bootstrap';

import { Namespace }               from "../../../../resources/namespaces/namespace";
import { Repository }              from "../../../../resources/respositories/repository";
import { RepositoryService }       from "../../../../resources/respositories/repository.service";
import { ProviderNamespace }       from "../../../../resources/provider-namespaces/provider-namespace";
import { RepositoryImportService } from "../../../../resources/repository-imports/repository-import.service";
import { RepositoryImport }        from "../../../../resources/repository-imports/repository-import";

import {
    AlternateNameModalComponent
} from "./alternate-name-modal/alternate-name-modal.component";

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

    @Input()
    set contentAdded(state: number) {
        // Get signal from parent when content added
        if (state != this._contentAdded) {
            this._contentAdded = state;
            console.log('Refreshing repositories');
            this.refreshRepositories();
        }
    }

    get contentChanged(): number {
        return this._contentAdded;
    }

    private _contentAdded: number;

    items: Repository[] = [new Repository()];   // init with one empty repo to preven EmptyState from flashing on the page
    
    emptyStateConfig: EmptyStateConfig;
    disabledStateConfig: EmptyStateConfig;

    listConfig: ListConfig;
    selectType: string = 'checkbox';
    loading: boolean = false;
    polling = null;
    bsModalRef: BsModalRef;

    constructor(
        private repositoryService: RepositoryService,
        private repositoryImportService: RepositoryImportService,
        private modalService: BsModalService
    ) {
        this.modalService.onHidden.subscribe(_ => {
            if (this.bsModalRef && this.bsModalRef.content.startedImport) {
                // Import started by AlternateNamedModalComponent
                console.log('Refreshing repositories...');
                this.refreshRepositories();
            }
        });
    }

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

        this.disabledStateConfig = {
            iconStyleClass: 'pficon-warning-triangle-o',
            info: `The Namespace ${this.namespace.name} is disabled. You'll need to re-enable it before viewing and modifying its content.`,
            title: 'Namespace Disabled'
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

        if (this.namespace.active) 
            this.getRepositories();
    }

    ngDoCheck(): void {}

    ngOnDestroy(): void {
        if (this.polling)
            this.polling.unsubscribe();
    }

    getActionConfig(item: Repository, importButtonTemplate: TemplateRef<any>): ActionConfig {
        let config = {
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
            }, {
                id: 'changeName',
                title: 'Change Name',
                tooltip: 'Change the repository name'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: true
        } as ActionConfig;

        // Set button disabled
        if (item['latest_import'] && (item['latest_import']['state'] === 'PENDING' || item['latest_import']['state'] === 'RUNNING')) {
            config.primaryActions[0].disabled = true;
            config.moreActionsVisible = false;
        }
        return config;
    }

    // Actions

    handleAction($event: Action, item: any): void {
        if (item) {
            switch ($event.id) {
                case 'import':
                    this.importRepository(item);
                    break;
                case 'delete':
                    this.deleteRepository(item);
                    break;
                case 'changeName':
                    this.changeRepositoryName(item);
                    break;
            }
        }
    }

    // Private

    private getRepositories() {
        this.loading = true;
        let queries: Observable<Repository[]>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            queries.push(this.repositoryService.query({ 'provider_namespace__id': pns.id, 'page_size': 1000}));
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
            
            if (this.items.length) {
                // If we have repositories, then track current import state via long polling
                setTimeout(_ => {
                    this.loading = false;
                    if (this.items.length) {
                        // Every 5 seconds, refresh the respository data
                        this.polling = Observable.interval(10000)
                            .subscribe(_ => {
                                this.refreshRepositories();
                            });
                    }
                }, 2000);
            } else {
                this.loading = false;
            }
        });
    }

    private refreshRepositories() {
        let queries: Observable<Repository[]>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            queries.push(this.repositoryService.query({'provider_namespace__id': pns.id, 'page_size': 1000}));
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
                        if (item.name != repo.name) {
                            item.name = repo.name;
                        }
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
        });
    }

    private importRepository(repository: Repository) {
        // Start an import
        repository['latest_import']['state'] = 'PENDING';
        repository['latest_import']['as_of_dt'] = '';
        this.repositoryImportService.save({'repository_id': repository.id})
            .subscribe(response => {
                    console.log(`Started import for repoostiroy ${repository.id}`);
            });
    }

    private deleteRepository(repository: Repository) {
        this.loading = true;
        this.repositoryService.destroy(repository).subscribe( _ =>{
            this.items.forEach((item: Repository, idx: number) => {
                if (item.id == repository.id) {
                    this.items.splice(idx, 1);
                    setTimeout(_ => {
                        this.loading = false;
                    }, 2000);
                }
            });
        });
    }

    private changeRepositoryName(repository: Repository) {
        const initialState = {
            repository: repository
        };
        this.bsModalRef = this.modalService.show(AlternateNameModalComponent, { initialState: initialState, keyboard: true, animated: true });
    }
}
