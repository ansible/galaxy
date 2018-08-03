import {
    Component,
    Input,
    OnDestroy,
    OnInit,
    TemplateRef,
    ViewEncapsulation,
} from '@angular/core';

import { flatten }           from 'lodash';
import { Action }            from 'patternfly-ng/action/action';
import { ActionConfig }      from 'patternfly-ng/action/action-config';
import { EmptyStateConfig }  from 'patternfly-ng/empty-state/empty-state-config';
import { ListConfig }        from 'patternfly-ng/list/basic-list/list-config';
import { ListEvent }         from 'patternfly-ng/list/list-event';

import {
    BsModalRef,
    BsModalService
} from 'ngx-bootstrap';

import { FilterConfig }                from 'patternfly-ng/filter/filter-config';
import { FilterField }                 from 'patternfly-ng/filter/filter-field';
import { FilterType }                  from 'patternfly-ng/filter/filter-type';

import { PaginationConfig }            from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent }             from 'patternfly-ng/pagination/pagination-event';
import { ToolbarConfig }               from 'patternfly-ng/toolbar/toolbar-config';

import { Namespace }               from '../../../../resources/namespaces/namespace';
import { PagedResponse }           from '../../../../resources/paged-response';
import { ProviderNamespace }       from '../../../../resources/provider-namespaces/provider-namespace';
import { Repository }              from '../../../../resources/repositories/repository';
import { RepositoryService }       from '../../../../resources/repositories/repository.service';
import { RepositoryImport }        from '../../../../resources/repository-imports/repository-import';
import { RepositoryImportService } from '../../../../resources/repository-imports/repository-import.service';

import {
    AlternateNameModalComponent
} from './alternate-name-modal/alternate-name-modal.component';

import 'rxjs/add/observable/interval';
import { Observable }              from 'rxjs/Observable';
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
        if (state !== this._contentAdded) {
            this._contentAdded = state;
            console.log('Refreshing repositories');
            this.refreshRepositories();
        }
    }

    get contentChanged(): number {
        return this._contentAdded;
    }

    private _contentAdded: number;

    items: Repository[] = [];

    emptyStateConfig: EmptyStateConfig;
    nonEmptyStateConfig: EmptyStateConfig;
    disabledStateConfig: EmptyStateConfig;
    paginationConfig: PaginationConfig = {
        pageSize: 10,
        pageNumber: 1,
        totalItems: 0,
    };
    maxItems = 0;

    listConfig: ListConfig;
    selectType = 'checkbox';
    loading = false;
    polling = null;
    bsModalRef: BsModalRef;

    filterConfig: FilterConfig;
    toolbarConfig: ToolbarConfig;
    isAscendingSort = true;

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
        const provider_namespaces = this.namespace.summary_fields.provider_namespaces;

        this.filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: FilterType.TEXT
                },
            ] as FilterField[],
            resultsCount: this.items.length,
            appliedFilters: []
        } as FilterConfig;

        this.toolbarConfig = {
            filterConfig: this.filterConfig,
            views: []
        } as ToolbarConfig;

        this.emptyStateConfig = {
            actions: {
                primaryActions: [],
                moreActions: []
            } as ActionConfig,
            iconStyleClass: 'pficon-warning-triangle-o',
            title: 'No Repositories',
            info: 'Add repositories by clicking the \'Add Content\' button above.',
            helpLink: {}
        } as EmptyStateConfig;

        this.nonEmptyStateConfig = {
            actions: {
                primaryActions: [],
                moreActions: []
            } as ActionConfig,
            iconStyleClass: '',
            title: '',
            info: '',
            helpLink: {}
        } as EmptyStateConfig;

        this.disabledStateConfig = {
            iconStyleClass: 'pficon-warning-triangle-o',
            info: `The Namespace ${this.namespace.name} is disabled. You'll need to re-enable it before viewing and modifying its content.`,
            title: 'Namespace Disabled'
        } as EmptyStateConfig;

        this.listConfig = {
            dblClick: false,
            emptyStateConfig: this.nonEmptyStateConfig,
            multiSelect: false,
            selectItems: false,
            selectionMatchProp: 'name',
            showCheckbox: false,
            useExpandItems: false
        } as ListConfig;

        if (this.namespace.active && provider_namespaces.length) {
            this.getRepositories();
        }
    }

    ngOnDestroy(): void {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    // Actions

    handleItemAction($event): void {
        const item = $event['item'] as Repository;
        if (item) {
            switch ($event['id']) {
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

    handlePageChange($event: PaginationEvent): void {
        if ($event.pageSize || $event.pageNumber) {
            this.loading = true;
            this.refreshRepositories();
        }
    }

    filterChanged($event): void {
        this.paginationConfig.pageNumber = 1;
        this.loading = true;
        this.refreshRepositories();
    }

    // Private

    private getRepositories() {
        this.loading = true;
        this.polling = Observable.interval(10000)
            .subscribe(pollingResult => {
                this.refreshRepositories();
            });
    }

    private getDetailUrl(item: Repository) {
        return `/${item.summary_fields['namespace']['name']}/${item.name}`;
    }

    private getIconClass(repository_format: string) {
        let result = 'pficon-repository list-pf-icon list-pf-icon-small';
        switch (repository_format) {
            case 'apb':
                result = 'pficon-bundle list-pf-icon list-pf-icon-small';
                break;
            case 'role':
                result = 'fa fa-gear list-pf-icon list-pf-icon-small';
                break;
        }
        return result;
    }

    private prepareRepository(item: Repository) {
        item['latest_import'] = {};
        item['detail_url'] = this.getDetailUrl(item);
        item['iconClass'] = this.getIconClass(item.format);
        if (item.summary_fields.latest_import) {
            item['latest_import'] = item.summary_fields.latest_import;
            if (item['latest_import']['finished']) {
                item['latest_import']['as_of_dt'] = moment(item['latest_import']['finished']).fromNow();
            } else {
                item['latest_import']['as_of_dt'] = moment(item['latest_import']['modified']).fromNow();
            }
        }
    }

    private refreshRepositories() {
        const queries: Observable<PagedResponse>[] = [];
        this.namespace.summary_fields.provider_namespaces.forEach((pns: ProviderNamespace) => {
            const query = {
                'provider_namespace__id': pns.id,
                'page_size': this.paginationConfig.pageSize,
                'page': this.paginationConfig.pageNumber,
            };

            if (this.filterConfig) {
                for (const filter of this.filterConfig.appliedFilters) {
                    query[`or__${filter.field.id}__icontains`] = filter.value;
                }
            }

            queries.push(this.repositoryService.pagedQuery(query));
        });

        forkJoin(queries).subscribe((results: PagedResponse[]) => {
            let repositories: Repository[] = [];

            let resultCount = 0;

            for (const response of results) {
                repositories =  repositories.concat(response.results as Repository[]);
                resultCount += response.count;
            }

            this.filterConfig.resultsCount = resultCount;
            this.paginationConfig.totalItems = resultCount;

            // maxItems is used to determine if we need to show the filter or not
            // it should never go down to avoid hiding the filter by accident when
            // a query returns a small number of items.
            if (this.maxItems < this.paginationConfig.totalItems) {
                this.maxItems = this.paginationConfig.totalItems;
            }

            // Generate a new list of repos
            const updatedList: Repository[] = [];
            repositories.forEach(repo => {
                this.prepareRepository(repo);
                updatedList.push(repo);
            });

            // set the old list to the new list to avoid screen flickering
            this.items = updatedList;
            this.loading = false;

            // Show blank screen during loads.
            this.updateEmptyState();
        });
    }

    private updateEmptyState(): void {
        if (this.items.length === 0) {
            this.listConfig.emptyStateConfig = this.emptyStateConfig;
        } else {
            this.listConfig.emptyStateConfig = this.nonEmptyStateConfig;
        }
    }

    private importRepository(repository: Repository) {
        // Start an import
        repository['latest_import']['state'] = 'PENDING';
        repository['latest_import']['as_of_dt'] = '';
        this.repositoryImportService.save({'repository_id': repository.id})
            .subscribe(response => {
                console.log(`Started import for repository ${repository.id}`);
            });
    }

    private deleteRepository(repository: Repository) {
        this.loading = true;
        this.repositoryService.destroy(repository).subscribe( _ => {
            this.items.forEach((item: Repository, idx: number) => {
                if (item.id === repository.id) {
                    this.items.splice(idx, 1);
                    this.loading = false;
                    this.updateEmptyState();
                }
            });
        });
    }

    private changeRepositoryName(repository: Repository) {
        const initialState = {
            repository: repository
        };
        this.bsModalRef = this.modalService.show(AlternateNameModalComponent,
            { initialState: initialState, keyboard: true, animated: true });
    }
}
