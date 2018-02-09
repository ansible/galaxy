import {
    Component,
    OnInit,
    TemplateRef,
    ViewEncapsulation,
    Input,
} from '@angular/core';

import { cloneDeep } from 'lodash';
import { flatten } from 'lodash';

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
import { forkJoin } from 'rxjs/observable/forkJoin';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'repositories-content',
    templateUrl: './repositories-content.component.html',
    styleUrls: ['./repositories-content.component.less']
})
export class RepositoriesContentComponent implements OnInit {
    @Input() namespace: Namespace;

    repositories: Repository[];
    emptyStateConfig: EmptyStateConfig;
    items: Repository[];
    itemsAvailable: boolean = true;
    listConfig: ListConfig;
    selectType: string = 'checkbox';
    loading: boolean = false;

    constructor(private repositoryService: RepositoryService,
                private repositoryImportService: RepositoryImportService) {
    }

    ngOnInit(): void {
        this.emptyStateConfig = {
            actions: {
                primaryActions: [],
                moreActions: []
            } as ActionConfig,
            iconStyleClass: 'pficon-warning-triangle-o',
            title: 'No Repositories',
            info: 'Add repositories by adding content to this namespace',
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

        this.getRepositories()
    }

    ngDoCheck(): void {
    }


    getActionConfig(item: Repository, actionButtonTemplate: TemplateRef<any>,
                    importButtonTemplate: TemplateRef<any>): ActionConfig {
        let actionConfig = {
            primaryActions: [{
                id: 'import',
                title: 'Import',
                tooltip: 'Import Repository',
                template: importButtonTemplate
            }],
            moreActions: [
            //{
            //     id: 'edit',
            //     title: 'Edit',
            //     tooltip: 'Edit Repository Properties'
            // },
            {
                id: 'delete',
                title: 'Delete',
                tooltip: 'Delete Repository'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: true
        } as ActionConfig;

        // Set button disabled
        // if (item.importing === true) {
        //     actionConfig.primaryActions[0].disabled = true;
        // }

        return actionConfig;
    }

    // Actions

    handleAction($event: Action, item: any): void {
        console.log('handleAction', $event, item);
        if ($event.id === 'import' && item) {
            this.importRepository(item);
        }
        if ($event.id == 'delete' && item) {
            console.log(`delete ${item.name}`);
        }
    }

    handleSelectionChange($event: ListEvent): void {
        console.log('handleSelectionChange', $event);
    }

    handleClick($event: ListEvent): void {
        console.log('handleClick', $event);
    }

    handleDblClick($event: ListEvent): void {
        console.log('handleDblClick', $event);
    }

    // Row selection

    updateItemsAvailable(): void {
        this.items = (this.itemsAvailable) ? cloneDeep(this.repositories) : [];
    }

    updateSelectionType(): void {
        if (this.selectType === 'checkbox') {
            this.listConfig.selectItems = false;
            this.listConfig.showCheckbox = true;
        } else if (this.selectType === 'row') {
            this.listConfig.selectItems = true;
            this.listConfig.showCheckbox = false;
        } else {
            this.listConfig.selectItems = false;
            this.listConfig.showCheckbox = false;
        }
    }

    private getRepositories() {
        this.loading = true;
        this.repositories = [];
        this.items = [];
        let queries: Observable<Repository[]>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            queries.push(this.repositoryService.query({
                provider_namespace: pns.id
            }));
        });

        forkJoin(queries).subscribe((results: Repository[][]) => {
            this.repositories = flatten(results);
            this.items = cloneDeep(this.repositories);
            this.loading = false;
        });

    }

    private importRepository(repository: Repository) {
        let repoImport: RepositoryImport = new RepositoryImport();
        repoImport.github_user = repository.github_user;
        repoImport.github_repo = repository.github_repo;
        this.repositoryImportService.save(repoImport)
            .subscribe(
                response => {
                    console.log(response);
                }
            );
    }
}
