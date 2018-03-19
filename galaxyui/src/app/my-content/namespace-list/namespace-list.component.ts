import {
    Component,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';


import { cloneDeep } from 'lodash';

import { Action }       from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';
import { ListEvent }    from 'patternfly-ng/list/list-event';
import { ListConfig }   from 'patternfly-ng/list/basic-list/list-config';

import { Namespace }                   from "../../resources/namespaces/namespace";
import { NamespaceService }            from "../../resources/namespaces/namespace.service";
import { BsModalService, BsModalRef }  from 'ngx-bootstrap';
import { AddRepositoryModalComponent } from "../add-repository-modal/add-repository-modal.component";
import { FilterConfig }                from "patternfly-ng/filter/filter-config";
import { ToolbarConfig }               from "patternfly-ng/toolbar/toolbar-config";
import { FilterType }                  from "patternfly-ng/filter/filter-type";
import { SortConfig }                  from "patternfly-ng/sort/sort-config";
import { FilterField }                 from "patternfly-ng/filter/filter-field";
import { SortField }                   from "patternfly-ng/sort/sort-field";
import { ToolbarView }                 from "patternfly-ng/toolbar/toolbar-view";
import { SortEvent }                   from "patternfly-ng/sort/sort-event";
import { Filter }                      from "patternfly-ng/filter/filter";
import { FilterEvent }                 from "patternfly-ng/filter/filter-event";


@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-list',
    templateUrl: './namespace-list.component.html',
    styleUrls: ['./namespace-list.component.less']
})
export class NamespaceListComponent implements OnInit {
    items: Namespace[];
    namespaces: Namespace[];

    pageTitle: string = "My Content";
    pageLoading: boolean = true;

    toolbarActionConfig: ActionConfig;
    filterConfig: FilterConfig;
    filtersText: string = '';
    isAscendingSort: boolean = true;
    sortConfig: SortConfig;
    currentSortField: SortField;
    toolbarConfig: ToolbarConfig;

    listActionConfig: ActionConfig;
    actionsText: string = '';
    listConfig: ListConfig;
    bsModalRef: BsModalRef;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private modalService: BsModalService,
        private namespaceService: NamespaceService
    ) {}

    ngOnInit(): void {
        this.route.data
            .subscribe((data: { namespaces: Namespace[] }) => {
                this.items = this.prepForList(data.namespaces);
                this.pageLoading = false;
            });

        this.filterConfig = {
            fields: [{
                id: 'name',
                title: 'Name',
                placeholder: 'Filter by Name...',
                type: FilterType.TEXT
            }] as FilterField[],
            resultsCount: this.items.length,
            appliedFilters: []
        } as FilterConfig;

        this.sortConfig = {
            fields: [{
                id: 'name',
                title: 'Name',
                sortType: 'alpha'
            }],
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

        this.listActionConfig = {
            primaryActions: [{
                id: 'addContent',
                styleClass: 'btn-primary',
                title: 'Add Content',
                tooltip: 'Add roles, modules, apbs and other content from repositories'
            }],
            moreActions: [{
                id: 'editNamespaceProps',
                title: 'Edit Properties',
                tooltip: 'Edit namespace properties'
            }, {
                id: 'deleteNamespace',
                title: 'Delete',
                tooltip: 'Delete Namespace'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: true
        } as ActionConfig;

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: false,
            selectionMatchProp: 'name',
            showCheckbox: false,
            useExpandItems: true
        } as ListConfig;
    }

    ngDoCheck(): void {}

    // Actions

    refreshNamespaces(): void {
        this.namespaceService.query()
            .subscribe(namespaces => this.items = namespaces);
    }

    handleToolbarAction(action: Action): void {
        this.actionsText = action.title + '\n' + this.actionsText;
    }

    optionSelected(option: number): void {
        this.actionsText = 'Option ' + option + ' selected\n' + this.actionsText;
        this.actionsText = 'Option ' + option + ' selected\n' + this.actionsText;
    }


    handleListAction($event: Action, item: any): void {
        switch ($event.id) {
            case 'addContent': {
                this.addContent(item);
                break;
            }
            case 'editNamespaceProps': {
                this.router.navigate([`/my-content/namespaces/${item.id}`]);
                break;
            }
            case 'deleteNamespace': {
                this.deleteNamespace(item);
                break;
            }
            default: {
                console.log(`handle action "${$event.id}" not found`, $event, item);
                console.log($event);
                console.log(item);
            }
        }
    }

    handleListClick($event: ListEvent): void {
        this.actionsText = $event.item.name + ' clicked\r\n' + this.actionsText;
    }

    // Filter

    applyFilters(filters: Filter[]): void {
        this.items = [];
        if (filters && filters.length > 0) {
            this.namespaces.forEach((item) => {
                if (this.matchesFilters(item, filters)) {
                    this.items.push(item);
                }
            });
        } else {
            this.items = this.namespaces;
        }
        this.toolbarConfig.filterConfig.resultsCount = this.items.length;
    }

    // Handle filter changes
    filterChanged($event: FilterEvent): void {
        this.filtersText = '';
        $event.appliedFilters.forEach((filter) => {
            this.filtersText += filter.field.title + ' : ' + filter.value + '\n';
        });
        this.applyFilters($event.appliedFilters);
        this.filterFieldSelected($event);
    }

    // Reset filtered queries
    filterFieldSelected($event: FilterEvent): void {
        //TODO
    }

    matchesFilter(item: any, filter: Filter): boolean {
        let match = true;
        if (filter.field.id === 'name') {
            match = item.name.match(filter.value) !== null;
        }

        return match;
    }

    matchesFilters(item: any, filters: Filter[]): boolean {
        let matches = true;
        filters.forEach((filter) => {
            if (!this.matchesFilter(item, filter)) {
                matches = false;
                return matches;
            }
        });
        return matches;
    }

    // Filter queries for type ahead
    filterQueries($event: FilterEvent) {
        return true;
    }

    // Sort

    compare(item1: any, item2: any): number {
        let compValue = 0;
        if (this.currentSortField.id === 'name') {
            compValue = item1.name.localeCompare(item2.name);
        }

        if (!this.isAscendingSort) {
            compValue = compValue * -1;
        }
        return compValue;
    }

    // Handle sort changes
    sortChanged($event: SortEvent): void {
        this.currentSortField = $event.field;
        this.isAscendingSort = $event.isAscending;
        this.items.sort((item1: any, item2: any) => this.compare(item1, item2));
    }

    // View

    viewSelected(currentView: ToolbarView): void {
        this.sortConfig.visible = (currentView.id === 'tableView' ? false : true);
    }


    //private

    private prepForList(namespaces: Namespace[]): Namespace[] {
        let clonedNamespaces = cloneDeep(namespaces);

        //TODO transform

        return clonedNamespaces;
    }

    private addContent(namespace: Namespace) {
        const initialState = {
            namespace: namespace
        };
        this.bsModalRef = this.modalService.show(AddRepositoryModalComponent, {initialState});
    }

    private deleteNamespace(namespace: Namespace) {
        this.namespaceService.delete(namespace)
            .subscribe(namespaces => {
                this.refreshNamespaces()
            });
    }
}
