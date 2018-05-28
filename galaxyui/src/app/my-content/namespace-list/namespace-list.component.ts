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
import { ListEvent }    from 'patternfly-ng/list/list-event';
import { ListConfig }   from 'patternfly-ng/list/basic-list/list-config';

import { Namespace }                   from "../../resources/namespaces/namespace";
import { NamespaceService }            from "../../resources/namespaces/namespace.service";
import { BsModalService, BsModalRef }  from 'ngx-bootstrap';
import { AddRepositoryModalComponent } from "../add-repository-modal/add-repository-modal.component";
import { Me }                          from "../../auth/auth.service";
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
    items: Namespace[] = [];
    namespaces: Namespace[] = [];
    me: Me;

    pageTitle: string = "My Content";
    pageLoading: boolean = true;

    toolbarActionConfig: ActionConfig;
    filterConfig: FilterConfig;
    filtersText: string = '';
    isAscendingSort: boolean = true;
    sortConfig: SortConfig;
    currentSortField: SortField;
    toolbarConfig: ToolbarConfig;

    actionsText: string = '';
    listConfig: ListConfig;
    bsModalRef: BsModalRef;

    contentAdded: number = 0;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private modalService: BsModalService,
        private namespaceService: NamespaceService
    ) {
        this.modalService.onHidden.subscribe(_ => {
            if (this.bsModalRef && this.bsModalRef.content.repositoriesAdded) {
                console.log('Content added.');
                this.contentAdded++;
            }
        });
    }

    ngOnInit(): void {
        this.route.data
            .subscribe(data => {
                this.me = data['me'];
                this.items = this.prepForList(data['namespaces']);
                this.namespaces = JSON.parse(JSON.stringify(this.items));
                this.cancelPageLoading();
            });

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
    }

    ngDoCheck(): void {}


    // Action Button and Menu

    getActionConfig(item: Namespace, addContentButtonTemplate: TemplateRef<any>): ActionConfig {
        let config = {
            primaryActions: [{
                id: 'addContent',
                title: 'Add Content',
                styleClass: 'btn-primary',
                tooltip: 'Add roles, modules, APBs and other content from repositories',
                template: addContentButtonTemplate
            }],
            moreActions: [{
                id: 'editNamespaceProps',
                title: 'Edit Properties',
                tooltip: 'Edit namespace properties'
            }, {
                id: 'disableNamespace',
                title: 'Disable',
                tooltip: 'Disable namespace'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: true
        } as ActionConfig;

        // Set disabled options
        if (!item.active) {
            config.primaryActions[0].disabled = true;
            config.moreActions[0].disabled = true;
            config.moreActions[1] = {
                id: 'enableNamespace',
                title: 'Enable',
                tooltip: 'Enable namespace'
            };
        }
        return config;
    }

    // Actions

    refreshNamespaces(): void {
        this.pageLoading = true;
        let params = {
            'page_size': 1000,
            'owners__username': this.me.username
        };
        this.namespaceService.query(params)
            .subscribe(namespaces => {
                this.items = this.prepForList(namespaces);
                this.namespaces = JSON.parse(JSON.stringify(this.items));
                this.cancelPageLoading();
            });
    }

    handleToolbarAction(action: Action): void {
        this.actionsText = action.title + '\n' + this.actionsText;
    }

    optionSelected(option: number): void {
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
            case 'disableNamespace':
            case 'enableNamespace': {
                this.enableDisableNamespace(item);
                break;
            }
            default: {
                console.log(`handle action "${$event.id}" not found`);
            }
        }
    }

    handleListClick($event: ListEvent): void {
        this.actionsText = $event.item.name + ' clicked\r\n' + this.actionsText;
    }

    filterChanged($event: FilterEvent): void {
        // Handle filter changes
        let filters = $event.appliedFilters;
        this.items = [];
        if (filters && filters.length > 0 && this.namespaces.length > 0) {
            this.namespaces.forEach((item) => {
                if (this.matchesFilters(item, filters)) {
                    this.items.push(JSON.parse(JSON.stringify(item)));
                }
            });
        } else {
            this.items = JSON.parse(JSON.stringify(this.namespaces));
        }
        this.toolbarConfig.filterConfig.resultsCount = this.items.length;
    }

    matchesFilter(item: any, filter: Filter): boolean {
        let match = true;
        if (filter.field.id === 'name') {
            match = item.name.toLowerCase().match(filter.value.toLowerCase()) !== null;
        } else if (filter.field.id == 'description') {
            match = item.description.toLowerCase().match(filter.value.toLowerCase()) !== null;
        }
        return match;
    }

    matchesFilters(item: any, filters: Filter[]): boolean {
        // Return true if all filters match the item.
        let matches = true;
        filters.forEach((filter) => {
            if (!this.matchesFilter(item, filter)) {
                matches = false;
                return matches;
            }
        });
        return matches;
    }


    // Sort
    compare(item1: any, item2: any): number {
        let compValue = 0;
        compValue = item1[this.currentSortField.id].localeCompare(item2[this.currentSortField.id]);
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
            .subscribe(_ => { this.refreshNamespaces() });
    }

    private cancelPageLoading(): void {
        setTimeout(_ => {
            this.pageLoading = false;
        }, 2000);
    }
}
