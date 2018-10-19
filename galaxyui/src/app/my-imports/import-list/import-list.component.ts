import {
    AfterViewInit,
    Component,
    InjectionToken,
    OnDestroy,
    OnInit,
    ViewChild,
} from '@angular/core';

import { ActivatedRoute } from '@angular/router';

import { Location } from '@angular/common';

import { ImportsService } from '../../resources/imports/imports.service';

import { interval } from 'rxjs';

import { Import } from '../../resources/imports/import';
import { ImportLatest } from '../../resources/imports/import-latest';

import { ImportState } from '../../enums/import-state.enum';
import { PagedResponse } from '../../resources/paged-response';

import { Filter } from 'patternfly-ng/filter/filter';
import { FilterConfig } from 'patternfly-ng/filter/filter-config';
import { FilterEvent } from 'patternfly-ng/filter/filter-event';
import { FilterField } from 'patternfly-ng/filter/filter-field';
import { FilterQuery } from 'patternfly-ng/filter/filter-query';
import { FilterType } from 'patternfly-ng/filter/filter-type';
import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';
import { ListComponent } from 'patternfly-ng/list/basic-list/list.component';

import { PaginationConfig } from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent } from 'patternfly-ng/pagination/pagination-event';

import { AuthService } from '../../auth/auth.service';

import * as $ from 'jquery';
import * as moment from 'moment';

@Component({
    selector: 'import-list',
    templateUrl: './import-list.component.html',
    styleUrls: ['./import-list.component.less'],
})
export class ImportListComponent implements OnInit, AfterViewInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'ImportListComponent';

    @ViewChild(ListComponent)
    pfList: ListComponent;

    listConfig: ListConfig;
    filterConfig: FilterConfig;
    locationParams: string;
    paginationConfig: PaginationConfig;

    items: ImportLatest[] = [];

    selected: Import = null;
    selectedId: number;
    checking = false;

    pageTitle = 'My Imports';
    pageIcon = 'fa fa-upload';
    pageLoading = true;
    refreshing = false;
    polling = null;
    filterParams = '';
    scroll: boolean;
    pageSize = 10;
    pageNumber = 1;
    appliedFilters: Filter[] = [];

    document: InjectionToken<Document>;

    constructor(
        private route: ActivatedRoute,
        private importsService: ImportsService,
        private location: Location,
        private authService: AuthService,
    ) {}

    ngOnInit() {
        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: true,
            showCheckbox: false,
            useExpandItems: false,
        } as ListConfig;

        this.filterConfig = {
            fields: [
                {
                    id: 'repository_name',
                    title: 'Repository Name',
                    placeholder: 'Filter by Repository Name...',
                    type: FilterType.TEXT,
                },
                {
                    id: 'namespace',
                    title: 'Namespace',
                    placeholder: 'Filter by Namespace...',
                    type: FilterType.TEXT,
                },
            ] as FilterField[],
            resultsCount: 0,
            appliedFilters: [],
        } as FilterConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0,
        } as PaginationConfig;

        this.route.queryParams.subscribe(params => {
            this.setPageSize(params);
            this.setAppliedFilters(params);
            this.setQuery();

            this.route.data.subscribe(data => {
                const imports: PagedResponse = data['imports'] as PagedResponse;
                this.items = imports.results;
                this.filterConfig.resultsCount = this.items.length;
                this.paginationConfig.totalItems = imports.count;
                this.prepareImports(this.items);
                if (this.items.length) {
                    if (params['selected']) {
                        this.getImport(Number(params['selected']), true);
                    } else {
                        this.getImport(this.items[0].id, true);
                    }
                } else {
                    this.cancelPageLoading();
                }
            });
            this.cancelPageLoading();
        });
    }

    ngAfterViewInit() {
        // this.setVerticalScroll();
        if (this.selected) {
            this.selectItem(this.selected.id);
        }
    }

    ngOnDestroy(): void {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize !== $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.searchImports();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber !== $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            if (this.pageSize === this.paginationConfig.pageSize) {
                // changed pageNumber without changing pageSize
                this.searchImports();
            }
        }
    }

    handleClick(event): void {
        if (event['item']) {
            const clickedId = event['item']['id'];
            if (clickedId !== this.selected.id) {
                if (this.polling) {
                    this.polling.unsubscribe();
                }
                this.getImport(clickedId, true);
            }
        }
    }

    selectItem(select: number, deselect?: number): void {
        this.items.forEach(item => {
            if (
                deselect !== null &&
                select !== deselect &&
                item.id === deselect
            ) {
                this.pfList.selectItem(item, false);
            } else if (item.id === select) {
                this.pfList.selectItem(item, true);
            }
        });
    }

    getImport(id: number, showPageLoader: boolean): void {
        if (showPageLoader) {
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
        this.importsService.get(id).subscribe(result => {
            this.prepareImport(result);
            this.selected = result;
            this.selectedId = result.id;
            this.setQuery();
            if (this.pfList) {
                this.selectItem(this.selected.id, deselectId);
            }
            this.cancelPageLoading();
            if (
                this.selected.state === ImportState.running ||
                this.selected.state === ImportState.pending
            ) {
                // monitor the state of a running import
                this.polling = interval(5000).subscribe(_ =>
                    this.refreshImport(),
                );
            }
        });
    }

    applyFilters($event: FilterEvent): void {
        this.filterParams = '';
        this.pageNumber = 1;
        this.paginationConfig.pageNumber = 1;
        if ($event.appliedFilters.length) {
            let query = '';
            let location = '';
            $event.appliedFilters.forEach((filter: Filter, idx: number) => {
                query += idx > 0 ? '&' : '';
                location += idx > 0 ? '&' : '';
                location += `${filter.field.id}=${filter.value.toLowerCase()}`;
                if (filter.field.id === 'namespace' && filter.value) {
                    query += `repository__provider_namespace__namespace__name__iexact=${filter.value.toLowerCase()}`;
                } else if (
                    filter.field.id === 'repository_name' &&
                    filter.value
                ) {
                    query += `repository__name__icontains=${filter.value.toLowerCase()}`;
                }
            });
            this.appliedFilters = JSON.parse(
                JSON.stringify($event.appliedFilters),
            );
            this.filterParams = query;
            this.locationParams = location;
        } else {
            this.appliedFilters = [];
            this.items = [];
            this.filterParams = '';
            this.locationParams = '';
        }
        this.selectedId = 0;
        this.searchImports();
    }

    startedImport($event): void {
        this.refreshImport();
        this.polling = interval(5000).subscribe(_ => this.refreshImport());
    }

    toggleScroll($event): void {
        this.scroll = $event;
        if (this.scroll) {
            this.scrollDetails();
        }
    }

    // private

    private scrollDetails() {
        const pgElement = document.getElementById('app-container');
        const detailHeight = document.getElementById('import-details-container')
            .scrollHeight;
        const pgHeight = pgElement.scrollHeight;
        const wHeight = window.innerHeight - 110;
        if (detailHeight > wHeight) {
            pgElement.scrollTop = pgHeight;
        }
    }

    private setPageSize(params: any) {
        if (params['page_size']) {
            this.paginationConfig.pageSize = params['page_size'];
            this.pageSize = params['page_size'];
            this.pageNumber = 1;
        }
        if (params['page']) {
            this.paginationConfig.pageNumber = params['page'];
            this.pageNumber = params['page'];
        }
    }

    private prepareImport(data: Import): void {
        if (!data.import_branch) {
            // TODO: a default value for import branch should be set on the backend
            data.import_branch = 'master';
            if (data.summary_fields.repository.import_branch) {
                data.import_branch =
                    data.summary_fields.repository.import_branch;
            }
        }
        if (data.state === ImportState.pending) {
            data.last_run = 'Waiting to start...';
        } else if (data.state === ImportState.running) {
            data.last_run = 'Running...';
        } else if (
            data.state === ImportState.failed ||
            data.state === ImportState.success
        ) {
            const state =
                data.state.charAt(0).toUpperCase() +
                data.state.slice(1).toLowerCase();
            data.last_run = state + ' ' + moment(data.finished).fromNow();
        }
    }

    private prepareImports(imports: ImportLatest[]): void {
        imports.forEach((item: ImportLatest) => {
            if (
                this.selected &&
                this.selected.summary_fields.repository.id === item.id
            ) {
                item['selected'] = true;
            }
            item.finished = moment(item.modified).fromNow();
            item.state =
                item.state.charAt(0).toUpperCase() +
                item.state.slice(1).toLowerCase();
        });
    }

    private getFilterField(id: string): FilterField {
        let result: FilterField = null;
        this.filterConfig.fields.forEach((item: FilterField) => {
            if (item.id === id) {
                result = item;
            }
        });
        return result;
    }

    private setAppliedFilters(queryParams: any) {
        // Convert query params to filters
        let filterParams = '';
        let location = '';
        const params = JSON.parse(JSON.stringify(queryParams));
        if (!params['namespace']) {
            params['namespace'] = this.authService.meCache.username;
        }
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                const field = this.getFilterField(key);
                if (!field) {
                    continue;
                }
                const values =
                    typeof params[key] === 'object'
                        ? params[key]
                        : [params[key]];
                values.forEach(value => {
                    if (filterParams !== '') {
                        filterParams += '&';
                        location += '&';
                    }
                    if (key === 'namespace') {
                        filterParams += `repository__provider_namespace__namespace__name__iexact=${value.toLowerCase()}`;
                        location += `${key}=${value.toLowerCase()}`;
                    } else if (key === 'repository_name') {
                        filterParams += `repository__name__icontains=${value.toLowerCase()}`;
                        location += `${key}=${value.toLowerCase()}`;
                    }
                    const ffield: Filter = {} as Filter;
                    ffield.field = field;
                    if (field.type === FilterType.TEXT) {
                        ffield.value = value;
                    } else if (field.type === FilterType.TYPEAHEAD) {
                        field.queries.forEach((query: FilterQuery) => {
                            if (query.id === value) {
                                ffield.query = query;
                                ffield.value = query.value;
                            }
                        });
                    }
                    this.filterConfig.appliedFilters.push(ffield);
                    this.appliedFilters.push(ffield);
                });
            }
        }
        this.filterParams = filterParams;
        this.locationParams = location;
    }

    private getBasePath(): string {
        const path = this.location.path();
        return path.replace(/\?.*$/, '');
    }

    private setQuery(): string {
        let paging = '&page_size=' + this.pageSize.toString();
        if (this.pageNumber > 1) {
            paging += '&page=' + this.pageNumber;
        }

        const query = (this.filterParams + paging).replace(/^&/, ''); // remove leading &
        const selected = this.selectedId ? `&selected=${this.selectedId}` : '';

        // Refresh params on location URL
        const location = (this.locationParams + selected + paging).replace(
            /^&/,
            '',
        ); // remove leading &
        this.location.replaceState(this.getBasePath(), location);

        return query;
    }

    private searchImports(): void {
        this.pageLoading = true;
        if (this.polling) {
            this.polling.unsubscribe();
        }
        const query = this.setQuery();
        this.importsService.latest(query).subscribe(results => {
            this.items = results.results;
            this.filterConfig.resultsCount = this.items.length;
            this.paginationConfig.totalItems = results.count;
            this.prepareImports(this.items);
            if (this.items.length) {
                this.getImport(this.items[0].id, true);
            } else {
                this.cancelPageLoading();
            }
        });
    }

    private refreshImport(): void {
        // Refresh the attributes of the currently selected import
        if (this.selected) {
            const selectedId = this.selected.id;
            this.refreshing = true;
            const params: any = {
                repository__id: this.selected.summary_fields.repository.id,
                order_by: '-id',
            };
            this.importsService.query(params).subscribe(result => {
                if (result.length) {
                    const import_result: Import = result[0];
                    this.prepareImport(import_result);
                    this.items.forEach((item: ImportLatest) => {
                        if (
                            item.repository_id ===
                            import_result.summary_fields.repository.id
                        ) {
                            item.finished = moment(
                                import_result.modified,
                            ).fromNow();
                            item.state =
                                import_result.state.charAt(0).toUpperCase() +
                                import_result.state.slice(1).toLowerCase();
                        }
                    });
                    if (this.selected.id === selectedId) {
                        // If the selected item has not changed,
                        //   copy result property values -> this.selected
                        const keys = Object.keys(import_result);
                        for (const key of keys) {
                            this.selected[key] = import_result[key];
                        }
                        if (
                            this.selected.state === ImportState.failed ||
                            this.selected.state === ImportState.success
                        ) {
                            // The import finished
                            if (this.polling) {
                                this.polling.unsubscribe();
                            }
                        }
                    }
                }
                this.refreshing = false;
                if (this.scroll) {
                    setTimeout(this.scrollDetails, 500);
                }
            });
        }
    }

    private cancelPageLoading(): void {
        this.pageLoading = false;
        this.refreshing = false;
    }
}
