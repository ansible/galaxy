import {
    Component,
    OnInit,
    TemplateRef,
    ViewEncapsulation
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';

import { cloneDeep }    from 'lodash';

import { Action }       from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';
import { ListConfig }   from 'patternfly-ng/list/basic-list/list-config';
import { ListEvent }    from 'patternfly-ng/list/list-event';

import { PaginationConfig }   from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent }    from 'patternfly-ng/pagination/pagination-event';

import { BsModalRef, BsModalService }  from 'ngx-bootstrap';
import { Filter }                      from 'patternfly-ng/filter/filter';
import { FilterConfig }                from 'patternfly-ng/filter/filter-config';
import { FilterEvent }                 from 'patternfly-ng/filter/filter-event';
import { FilterField }                 from 'patternfly-ng/filter/filter-field';
import { FilterType }                  from 'patternfly-ng/filter/filter-type';
import { SortConfig }                  from 'patternfly-ng/sort/sort-config';
import { SortEvent }                   from 'patternfly-ng/sort/sort-event';
import { SortField }                   from 'patternfly-ng/sort/sort-field';
import { ToolbarConfig }               from 'patternfly-ng/toolbar/toolbar-config';
import { ToolbarView }                 from 'patternfly-ng/toolbar/toolbar-view';
import { Me }                          from '../../auth/auth.service';
import { AuthService }                 from '../../auth/auth.service';
import { Namespace }                   from '../../resources/namespaces/namespace';
import { NamespaceService }            from '../../resources/namespaces/namespace.service';
import { PagedResponse }               from '../../resources/paged-response';
import { AddRepositoryModalComponent } from '../add-repository-modal/add-repository-modal.component';


@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-list',
    templateUrl: './namespace-list.component.html',
    styleUrls: ['./namespace-list.component.less']
})
export class NamespaceListComponent implements OnInit {
    items: Namespace[] = [];
    namespaces: Namespace[] = [];
    me: Me;

    pageTitle = 'My Content';
    pageIcon = 'fa fa-list';
    pageLoading = true;

    toolbarActionConfig: ActionConfig;
    filterConfig: FilterConfig;
    filtersText = '';
    isAscendingSort = true;
    sortConfig: SortConfig;
    currentSortField: SortField;
    toolbarConfig: ToolbarConfig;
    paginationConfig: PaginationConfig;

    pageNumber = 1;
    pageSize = 10;

    actionsText = '';
    listConfig: ListConfig;
    bsModalRef: BsModalRef;

    filterBy: any = {};
    sortBy = 'name';

    contentAdded = 0;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private modalService: BsModalService,
        private namespaceService: NamespaceService,
        private authService: AuthService
    ) {
        this.modalService.onHidden.subscribe(_ => {
            if (this.bsModalRef && this.bsModalRef.content.repositoriesAdded) {
                console.log('Content added.');
                this.contentAdded++;
            }
        });
    }

    ngOnInit(): void {
        if (!this.authService.meCache.staff) {
            this.filterBy['owners__username'] = this.authService.meCache.username;
        }

        this.filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: FilterType.TEXT
                },
                {
                    id: 'description',
                    title: 'Description',
                    placeholder: 'Filter by Description...',
                    type: FilterType.TEXT
                }
            ] as FilterField[],
            resultsCount: this.items.length,
            appliedFilters: []
        } as FilterConfig;

        this.sortConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    sortType: 'alpha'
                },
                {
                    id: 'description',
                    title: 'Description',
                    sortType: 'alpha'
                }
            ],
            isAscending: this.isAscendingSort
        } as SortConfig;

        this.toolbarActionConfig = {
            primaryActions: [],
            moreActions: []
        } as ActionConfig;

        this.toolbarConfig = {
            actionConfig: this.toolbarActionConfig,
            filterConfig: this.filterConfig,
            sortConfig: this.sortConfig,
            views: []
        } as ToolbarConfig;

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: false,
            selectionMatchProp: 'name',
            showCheckbox: false,
            useExpandItems: true
        } as ListConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0
        } as PaginationConfig;

        this.route.data
            .subscribe(data => {
                const results = data['namespaces'] as PagedResponse;
                this.me = data['me'];
                this.items = this.prepForList(results.results as Namespace[]);
                this.filterConfig.resultsCount = results.count;
                this.paginationConfig.totalItems = results.count;
                this.pageLoading = false;
            });
    }

    handleListAction($event: any): void {
        const item = $event['item'] as Namespace;
        switch ($event['id']) {
            case 'addContent':
                this.addContent(item);
                break;
            case 'editNamespaceProps':
                this.router.navigate([`/my-content/namespaces/${item.id}`]);
                break;
            case 'disableNamespace':
            case 'enableNamespace':
                this.enableDisableNamespace(item);
                break;
            case 'deleteNamespace':
                this.deleteNamespace(item);
                break;
            default:
                console.log(`handle action "${$event['id']}" not found`);
        }
    }

    filterChanged($event): void {
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach(filter => {
                if (filter.field.type === 'typeahead') {
                    this.filterBy['or__' + filter.field.id + '__icontains'] = filter.query.id;
                } else {
                    this.filterBy['or__' + filter.field.id + '__icontains'] = filter.value;
                }
            });
        } else {
            this.filterBy = {};
            if (!this.authService.meCache.staff) {
                this.filterBy['owners__username'] = this.authService.meCache.username;
            }
        }
        this.pageNumber = 1;
        this.searchNamespaces();
    }

    sortChanged($event: SortEvent): void {
        if ($event.isAscending) {
            this.sortBy = $event.field.id;
        } else {
            this.sortBy = '-' + $event.field.id;
        }
        this.searchNamespaces();
    }

    // View

    viewSelected(currentView: ToolbarView): void {
        this.sortConfig.visible = (currentView.id === 'tableView' ? false : true);
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.searchNamespaces();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            if (this.pageSize === this.paginationConfig.pageSize) {
                // changed pageNumber without changing pageSize
                this.searchNamespaces();
            }
        }
    }

    // private

    private prepForList(namespaces: Namespace[]): Namespace[] {
        const clonedNamespaces = cloneDeep(namespaces);
        return clonedNamespaces;
    }

    private addContent(namespace: Namespace) {
        const initialState = {
            namespace: namespace
        };
        this.bsModalRef = this.modalService.show(AddRepositoryModalComponent, {initialState: initialState, keyboard: true, animated: true});
    }

    private enableDisableNamespace(namespace: Namespace) {
        namespace.active = !namespace.active;
        this.namespaceService.save(namespace)
            .subscribe(_ => { this.searchNamespaces(); });
    }

    private searchNamespaces() {
        this.pageLoading = true;
        this.filterBy['page_size'] = this.pageSize;
        this.filterBy['page'] = this.pageNumber;
        this.filterBy['order'] = this.sortBy;
        this.namespaceService.pagedQuery(this.filterBy).subscribe(result => {
            this.items = this.prepForList(result.results as Namespace[]);
            this.filterConfig.resultsCount = result.count;
            this.paginationConfig.totalItems = result.count;
            this.pageLoading = false;
        });
    }

    private deleteNamespace(namespace: Namespace) {
        this.namespaceService.delete(namespace).subscribe(result => {
            this.searchNamespaces();
        });
    }
}
