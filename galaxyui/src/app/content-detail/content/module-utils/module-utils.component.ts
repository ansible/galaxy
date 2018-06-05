import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { EmptyStateConfig }  from 'patternfly-ng/empty-state/empty-state-config';

import { ListEvent }         from 'patternfly-ng/list/list-event';
import { ListConfig }        from 'patternfly-ng/list/basic-list/list-config';

import { Content }           from '../../../resources/content/content';
import { ContentService }    from '../../../resources/content/content.service';
import { Repository }        from '../../../resources/repositories/repository';
import { PagedResponse }     from '../../../resources/paged-response';

import { ContentTypes }      from '../../../enums/content-types.enum';

import { FilterConfig }      from 'patternfly-ng/filter/filter-config';
import { FilterField }       from 'patternfly-ng/filter/filter-field';
import { FilterEvent }       from 'patternfly-ng/filter/filter-event';
import { FilterQuery }       from 'patternfly-ng/filter/filter-query';
import { FilterType }        from 'patternfly-ng/filter/filter-type';
import { Filter }            from "patternfly-ng/filter/filter";

import { PaginationConfig }  from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent }   from 'patternfly-ng/pagination/pagination-event';

import { Observable }        from "rxjs/Observable";
import { forkJoin }          from 'rxjs/observable/forkJoin';


@Component({
    selector: 'module-utils-detail',
    templateUrl: './module-utils.component.html',
    styleUrls: ['./module-utils.component.less']
})
export class ModuleUtilsComponent implements OnInit {

    constructor(
        private contentService: ContentService
    ) {}

    emptyStateConfig: EmptyStateConfig;
    filterConfig: FilterConfig;
    listConfig: ListConfig;
    paginationConfig: PaginationConfig;
    pageSize: number = 10;
    pageNumber: number = 1;
    query: string;
    items: Content[] = [];
    loading: Boolean = true;
    _selectedContent: Content;
    _modules: Content[];
    _repository: Repository;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    @Input()
    set selectedContent(data: Content) {
        if (data && data.content_type == ContentTypes.moduleUtils) {
            this._selectedContent = data;
            if (this.filterConfig && this.filterConfig.fields) {
                this.filterConfig.appliedFilters.push({
                    field: this.filterConfig.fields[0],
                    value: this._selectedContent.name
                } as Filter);
                this.queryContentList(this._selectedContent.name);
            }
        }
    }

    get selectedContent(): Content {
        return this._selectedContent;
    }

    ngOnInit() {
        this.emptyStateConfig = {
            iconStyleClass: 'pficon-warning-triangle-o',
            info: 'This plugin does not contain any documentation or metadata.',
            title: 'No Metdata Found'
        } as EmptyStateConfig;

        this.listConfig = {
            dblClick: false,
            multiSelect: false,
            selectItems: false,
            showCheckbox: false,
            useExpandItems: true
        } as ListConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0
        } as PaginationConfig;

        this.filterConfig = {
            fields: [{
                id: 'name',
                title: 'Name',
                placeholder: 'Filter by Name...',
                type: FilterType.TEXT,
            }, {
                id: 'description',
                title: 'Description',
                placeholder: 'Filter by Description...',
                type: FilterType.TEXT,
            }] as FilterField[],
            resultsCount: 0,
            appliedFilters: []
        } as FilterConfig;

        if (this._selectedContent) {
            this.filterConfig.appliedFilters.push({
                field: this.filterConfig.fields[0],
                value: this._selectedContent.name
            } as Filter);
        }

        this.queryContentList((this.selectedContent) ? this.selectedContent.name : null);
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize != $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.queryContentList();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber != $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            this.queryContentList();
        }
    }

    applyFilters($event: FilterEvent) {
        let params: string[] = []
        let query: string = null;
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach((filter: Filter) => {
                params.push(`or__${filter.field.id}__icontains=${filter.value.toLowerCase()}`);
            });
            query = '?' + params.join('&');
        }
        this.query = query;
        this.queryContentList();
    }


    // private

    private queryContentList(contentName?: string) {
        this.loading = true;
        let queryString = (this.query) ? this.query : '?';
        let params = {
            'page_size': this.pageSize,
            'page': this.pageNumber,
            'content_type__name': ContentTypes.moduleUtils,
            'repository__id': this.repository.id
        };
        if (contentName) {
            params['name'] = contentName;
        }
        let _tmp = [];
        for (var key in params) {
            _tmp.push(`${key}=${params[key]}`);
        }
        queryString += (queryString == '?') ? _tmp.join('&') : '&' + _tmp.join('&');
        this.contentService.pagedQuery(queryString).subscribe(
            results => {
                this._modules = results.results as Content[];
                this.filterConfig.resultsCount = results.count;
                this.paginationConfig.totalItems = results.count;
                this.getContentDetail();
            }
        )
    }

    private getContentDetail() {
        if (!this._modules || !this._modules.length) {
            this.items = [];
            this.loading = false;
            return;
        }

        let queries: Observable<Content>[] = [];
        this._modules.forEach((module: Content) => {
            queries.push(this.contentService.get(module.id));
        });

        forkJoin(queries).subscribe((results: Content[]) => {
            this.items = JSON.parse(JSON.stringify(results));
            this.items.forEach(item => {
                item['moduleStatus'] = null;
                item['moduleSupport'] = null;

                if (item.metadata['ansible_metadata']) {
                    let metadata = item.metadata['ansible_metadata'];
                    item['moduleStatus'] = metadata['status'].join(', ');
                    item['moduleSupport'] = metadata['supported_by'];
                }
            });
            this.loading = false;
        });
    }
}
