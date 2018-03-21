import {
    Component,
    OnInit,
    ViewChild,
    AfterViewInit,
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';

import {
    ImportsService,
    SaveParams
} from '../../resources/imports/imports.service';

import { Import }        from '../../resources/imports/import';
import { ImportLatest }  from '../../resources/imports/import-latest';

import { PageHeaderComponent } from '../../page-header/page-header.component';

import { ListConfig }    from 'patternfly-ng/list/basic-list/list-config';
import { ListEvent }     from 'patternfly-ng/list/list-event';
import { ListComponent } from 'patternfly-ng/list/basic-list/list.component';
import { FilterConfig }  from 'patternfly-ng/filter/filter-config';
import { FilterField }   from 'patternfly-ng/filter/filter-field';
import { FilterEvent }   from 'patternfly-ng/filter/filter-event';
import { FilterQuery }   from 'patternfly-ng/filter/filter-query';
import { FilterType }    from 'patternfly-ng/filter/filter-type';
import { Filter }        from "patternfly-ng/filter/filter";

import * as moment       from 'moment';

@Component({
    selector: 'import-list',
    templateUrl: './import-list.component.html',
    styleUrls: ['./import-list.component.less']
})
export class ImportListComponent implements OnInit, AfterViewInit {

    @ViewChild(ListComponent) pfList: ListComponent;

    listConfig: ListConfig;
    filterConfig: FilterConfig;

    items: ImportLatest[] = [];
    selected: Import = null;
    checking: boolean = false;

    pageTitle: string = "My Imports";
    pageLoading: boolean = true;

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private importsService: ImportsService
    ){}

    ngOnInit() {
        this.route.data.subscribe(
            (data) => {
                this.items = data['imports'];
                this.prepareImports(this.items);
                if (this.items.length) {
                    this.getImport(this.items[0].id);
                } else {
                    this.pageLoading = false;
                }
            }
        );

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: true,
            showCheckbox: false,
            useExpandItems: false
        } as ListConfig;

        this.filterConfig = {
            fields: [{
                id: 'repository_name',
                title: 'Repository Name',
                placeholder: 'Filter by Repository Name...',
                type: FilterType.TEXT,
            }, {
                id: 'namespace',
                title: 'Namespace',
                placeholder: 'Filter by Namespace...',
                type: FilterType.TEXT,
            }] as FilterField[],
            resultsCount: this.items.length,
            appliedFilters: []
        } as FilterConfig;

        this.route.queryParams.subscribe(params => {
            if (params['namespace']) {
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[1],
                    value: params['namesspace']
                });
            }
            if (params['repository_name']) {
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[0],
                    value: params['repository_name']
                });
            }
        });
    }

    ngAfterViewInit() {
        if (this.selected) {
            this.selectItem(this.selected.id);
        }
    }

    handleAction(event, msg): void {}

    handleClick(event): void {
        if (event['item']) {
            let clickedId = event['item']['id'];
            if (clickedId != this.selected.id) {
                this.getImport(clickedId);
            }
        }
    }

    selectItem(select: number, deselect?: number): void {
        this.items.forEach(item => {
            if (deselect != null && item.id == deselect) {
                this.pfList.selectItem(item, false);
            } else if (item.id == select) {
                this.pfList.selectItem(item, true);
            }
        });
    }

    getImport(id: number): void {
        this.pageLoading = true;
        this.importsService.get(id).subscribe(
            result => {
                let deselectId = this.selected  ? this.selected.id : null;
                this.selected = result;
                this.pageLoading = false;
                if (!this.selected.import_branch) {
                    // TODO: a default value for import branch should be set on the backend
                    this.selected.import_branch = "master";
                    if (this.selected.summary_fields.repository.import_branch) {
                        this.selected.import_branch = this.selected.summary_fields.repository.import_branch;
                    }
                }
                if (this.selected.state == 'PENDING') {
                    this.selected.last_run = "Waiting to start...";
                }
                else if (this.selected.state == 'RUNNING') {
                    this.selected.last_run = "Running...";
                }
                else if (this.selected.finished) {
                    this.selected.last_run = 'Finished ' + moment(this.selected.finished).fromNow();
                }
                if (this.pfList) {
                    this.selectItem(this.selected.id, deselectId);
                }
            });
    }

    applyFilters(filters: FilterEvent): void {
        console.log(filters);
        if (filters.appliedFilters.length) {
            let query = '';
            filters.appliedFilters.forEach((filter: Filter, idx: number) => {
                query += idx > 0 ? '&' : '';
                if (filter.field.id == 'namespace' && filter.value) {
                    query += `or__repository__provider_namespace__namespace__name__icontains=${filter.value.toLowerCase()}`;
                } else if (filter.field.id == 'repository_name' && filter.value) {
                    query += `or__repository__name__icontains=${filter.value.toLowerCase()}`;
                }
            });
            this.searchImports(query);
        } else {
            this.searchImports();
        }
    }

    // private 

    private searchImports(query?: string): void {
        this.pageLoading = true;
        this.importsService.latest(query).subscribe(results => {
            this.items = results;
            this.prepareImports(this.items);
            this.filterConfig.resultsCount = this.items.length;
            if (this.items.length) {
                this.getImport(this.items[0].id);
            } else {
                this.pageLoading = false;
            }
        });
    }

    private prepareImports(imports: ImportLatest[]): void {
        imports.forEach(item => {
            item.finished = moment(item.modified).fromNow();
            item.state = item.state.charAt(0).toUpperCase() + item.state.slice(1).toLowerCase();
        });
    }
}
