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

import { Observable }    from "rxjs/Observable";

import { Import }        from '../../resources/imports/import';
import { ImportLatest }  from '../../resources/imports/import-latest';

import { ImportState }   from '../../enums/import-state.enum';

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
import * as $            from 'jquery';

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
    refreshing: boolean = false;
    polling = null;
    query: string;
    scroll: boolean;

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
                    this.getImport(this.items[0].id, true);
                } else {
                    this.cancelPageLoading();
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
            let event: FilterEvent = new FilterEvent();
            event.appliedFilters = [];
            if (params['namespace']) {
                event.appliedFilters.push({
                    field: this.filterConfig.fields[1],
                    value: params['namesspace']
                } as Filter);
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[1],
                    value: params['namesspace']
                } as Filter);
            }
            if (params['repository_name']) {
                event.appliedFilters.push({
                    field: this.filterConfig.fields[0],
                    value: params['repository_name']
                } as Filter);
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[1],
                    value: params['namesspace']
                } as Filter);
            }
            if (event.appliedFilters.length) {
                this.applyFilters(event);
            }
        });
    }

    ngAfterViewInit() {
        this.setVerticalScroll();
        if (this.selected) {
            this.selectItem(this.selected.id);
        }
    }

    ngOnDestroy(): void {
        if (this.polling)
            this.polling.unsubscribe();
    }

    handleAction(event, msg): void {}

    handleClick(event): void {
        if (event['item']) {
            let clickedId = event['item']['id'];
            if (clickedId != this.selected.id) {
                if (this.polling) {
                    this.polling.unsubscribe();
                }
                this.getImport(clickedId, true);
            }
        }
    }

    selectItem(select: number, deselect?: number): void {
        this.items.forEach(item => {
            if (deselect != null && select != deselect && item.id == deselect) {
                this.pfList.selectItem(item, false);
            } else if (item.id == select) {
                this.pfList.selectItem(item, true);
            }
        });
    }

    getImport(id: number, showPageLoader: boolean): void {
        if(showPageLoader) {
            this.pageLoading = true;
        }
        let deselectId: number;
        if (this.selected) {
            deselectId = this.selected.id;
            this.selected.id = 0;
        }
        if (this.polling) {
            this.polling.unsubscribe();
        }
        this.importsService.get(id).subscribe(
            result => {
                this.prepareImport(result)
                this.selected = result;
                if (this.pfList) {
                    this.selectItem(this.selected.id, deselectId);
                }
                this.cancelPageLoading();
                setTimeout(_ => { this.setVerticalScroll(); }, 1000);
                if (this.selected.state == ImportState.running ||
                    this.selected.state == ImportState.pending) {
                        // monitor the state of a running import
                        this.polling = Observable.interval(5000)
                            .subscribe(_ => this.refreshImport());
                }
            });
    }

    applyFilters(filters: FilterEvent): void {
        this.query = null;
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
            this.query = query;
            console.log('this.query: ' + this.query);
        }
        this.searchImports(this.query);
    }

    onResize($event): void {
        // On browser resize
        this.setVerticalScroll();
    }

    startedImport($event): void {
        this.refreshImport();
        this.polling = Observable.interval(5000)
            .subscribe(_ => this.refreshImport());
    }

    toggleScroll($event): void {
        this.scroll = $event;
        if (this.scroll) {
            this.scrollDetails();
        }
    }

    // private

    private scrollDetails() {
        $('#import-details-container').animate({scrollTop:$('#import-details-container')[0].scrollHeight}, 1000);
    }

    private prepareImport(data: Import): void {
        if (!data.import_branch) {
            // TODO: a default value for import branch should be set on the backend
            data.import_branch = "master";
            if (data.summary_fields.repository.import_branch) {
                data.import_branch = data.summary_fields.repository.import_branch;
            }
        }
        if (data.state == ImportState.pending) {
            data.last_run = "Waiting to start...";
        }
        else if (data.state == ImportState.running) {
            data.last_run = "Running...";
        }
        else if (data.state == ImportState.failed || data.state == ImportState.success) {
            let state = data.state.charAt(0).toUpperCase() +
                data.state.slice(1).toLowerCase();
            data.last_run = state + ' ' + moment(data.finished).fromNow();
        }
    }

    private prepareImports(imports: ImportLatest[]): void {
        imports.forEach((item: ImportLatest) => {
            if (this.selected && this.selected.summary_fields.repository.id == item.id) {
                item['selected'] = true;
            }
            item.finished = moment(item.modified).fromNow();
            item.state = item.state.charAt(0).toUpperCase() + item.state.slice(1).toLowerCase();
        });
    }

    private setVerticalScroll(): void {
        let windowHeight = window.innerHeight;
        let windowWidth = window.innerWidth;
        let $importList = $('#import-list');
        let $importDetails = $('#import-details-container');
        if (windowWidth > 768) {
            let headerh = $('.page-header').outerHeight(true);
            let navbarh = $('.navbar-pf-vertical').outerHeight(true);
            let filterh = $('#import-filter').outerHeight(true);
            let listHeight = windowHeight - headerh - navbarh - filterh - 60;
            if (!isNaN(listHeight)) {
                $importList.css('height', listHeight);
            }

            let detailHeight = windowHeight - headerh - navbarh - 60;
            if (!isNaN(detailHeight)) {
                $importDetails.css('height', detailHeight);
            }
        } else {
            $importList.css('height', '100%');
            $importDetails.css('height', '100%');
        }
        if (this.scroll) {
             this.scrollDetails();
        }
    }

    private searchImports(query?: string): void {
        this.pageLoading = true;
        if (this.polling) {
            this.polling.unsubscribe();
        }
        this.importsService.latest(query).subscribe(results => {
            this.items = results;
            this.prepareImports(this.items);
            this.filterConfig.resultsCount = this.items.length;
            if (this.items.length) {
                this.getImport(this.items[0].id, true);
            } else {
                this.cancelPageLoading();
            }
            setTimeout(_ => { this.setVerticalScroll(); }, 1000);
        });
    }

    private refreshImport(): void {
        // Refresh the attributes of the currently selected import
        if (this.selected) {
            let selectedId = this.selected.id;
            this.refreshing = true;
            let params: any = {
                'repository__id': this.selected.summary_fields.repository.id,
                'order_by': '-id'
            }
            this.importsService.query(params).subscribe(
                result => {
                    if (result.length) {
                        let import_result: Import = result[0];
                        this.prepareImport(import_result);
                        this.items.forEach((item: ImportLatest) => {
                            if (item.repository_id == import_result.summary_fields.repository.id) {
                                item.finished = moment(import_result.modified).fromNow();
                                item.state = import_result.state.charAt(0).toUpperCase() +
                                    import_result.state.slice(1).toLowerCase();
                            }
                        });
                        if (this.selected.id == selectedId) {
                            // If the selected item has not changed,
                            //   copy result property values -> this.selected
                            let keys = Object.keys(import_result);
                            for (var i=0; i < keys.length; i++ ) {
                                this.selected[keys[i]] = import_result[keys[i]];
                            }
                            if (this.selected.state == ImportState.failed ||
                                this.selected.state == ImportState.success) {
                                // The import finished
                                if (this.polling) {
                                    this.polling.unsubscribe();
                                }
                            }
                        }
                    }
                    this.refreshing = false;
                    if (this.scroll)
                        this.scrollDetails();
                    setTimeout(_ => { this.setVerticalScroll(); }, 1000);
                });
        }
    }

    private cancelPageLoading(): void {
        setTimeout(_ => {
            this.pageLoading = false;
            this.refreshing = false;
        }, 500);
    }
}
