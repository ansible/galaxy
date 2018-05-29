import {
	Component,
	OnInit
} from '@angular/core';

import {
	ActivatedRoute,
	Router
} from '@angular/router';

import * as moment            from 'moment';

import { Action }             from 'patternfly-ng/action/action';
import { ActionConfig }       from 'patternfly-ng/action/action-config';
import { ListEvent }          from 'patternfly-ng/list/list-event';
import { ListConfig }         from 'patternfly-ng/list/basic-list/list-config';
import { FilterConfig }       from "patternfly-ng/filter/filter-config";
import { ToolbarConfig }      from "patternfly-ng/toolbar/toolbar-config";
import { FilterType }         from "patternfly-ng/filter/filter-type";
import { SortConfig }         from "patternfly-ng/sort/sort-config";
import { FilterField }        from "patternfly-ng/filter/filter-field";
import { SortField }          from "patternfly-ng/sort/sort-field";
import { ToolbarView }        from "patternfly-ng/toolbar/toolbar-view";
import { SortEvent }          from "patternfly-ng/sort/sort-event";
import { Filter }             from "patternfly-ng/filter/filter";
import { FilterEvent }        from "patternfly-ng/filter/filter-event";
import { EmptyStateConfig }   from "patternfly-ng/empty-state/empty-state-config";
import { PaginationConfig }   from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent }    from 'patternfly-ng/pagination/pagination-event';

import { Namespace }          from '../../resources/namespaces/namespace';

import { RepositoryService }  from '../../resources/repositories/repository.service';
import { Repository }         from '../../resources/repositories/repository';

import {
    ContentTypes,
    ContentTypesPluralChoices,
    ContentTypesIconClasses
} from '../../enums/content-types.enum';

import {
    RepoFormats,
    RepoFormatsTooltips,
    RepoFormatsIconClasses
} from '../../enums/repo-types.enum';


@Component({
    selector: 'app-author-detail',
    templateUrl: './author-detail.component.html',
    styleUrls: ['./author-detail.component.less']
})
export class AuthorDetailComponent implements OnInit {

    constructor(
    	private router: Router,
  	    private route: ActivatedRoute,
  	    private repositoryService: RepositoryService
    ) {}

    pageTitle: string = '';
    pageLoading: boolean = true;

    namespace: Namespace;
    items: Repository[] = [];

    emptyStateConfig: EmptyStateConfig;
    nameEmptyStateConfig: EmptyStateConfig;
    authorNotFound: boolean = false;
    toolbarActionConfig: ActionConfig;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
    toolbarConfig: ToolbarConfig;
    listConfig: ListConfig;
    paginationConfig: PaginationConfig;

    pageSize: number = 10;
    pageNumber: number = 1;
    filterBy: any = {};
    sortBy: string = 'name';

    RepoFormats: typeof RepoFormats = RepoFormats;

    ngOnInit() {

        this.emptyStateConfig = {
            info: '',
            title: 'No repositories match your search',
            iconStyleClass: 'pficon pficon-filter'
        } as EmptyStateConfig;

        this.nameEmptyStateConfig = {
            title: 'Author not found!',
            info: 'The requested content author was not found. Try using the Search page to browse  ' +
            'available content.',
            iconStyleClass: 'pficon-warning-triangle-o',
            helpLink: {
                hypertext: 'Visit the Search page',
                text: '',
                url: '/search'
            },
        } as EmptyStateConfig;

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
            resultsCount: 0,
            appliedFilters: [] as Filter[]
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
            isAscending: true
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
            useExpandItems: false,
            emptyStateConfig: this.emptyStateConfig
        } as ListConfig;

        this.paginationConfig = {
            pageSize: 10,
            pageNumber: 1,
            totalItems: 0
        } as PaginationConfig;

        this.route.data.subscribe((data) => {
            this.namespace = data['namespace'];
            this.items = data['repositories']['results'];
            this.paginationConfig.totalItems = data['repositories']['count'];
            if (this.namespace && this.namespace.name) {
                if (this.namespace.is_vendor) {
                    this.pageTitle = `<i class="fa fa-star"></i> Vendors;/vendors;${this.namespace.name}`;
                } else {
                    this.pageTitle = `<i class="fa fa-users"></i> Community Authors;/authors;${this.namespace.name}`;
                }
                this.parepareNamespace();
            } else {
                this.authorNotFound = true;
            }
            if (this.items && this.items.length) {
                this.prepareRepositories();
            }
            this.pageLoading = false;
        });
    }

    handleListClick($event: ListEvent): void {
        let repository = $event.item;
        this.router.navigate(['/', repository.summary_fields['namespace']['name'],
                    repository.name]);
    }

    filterChanged($event: FilterEvent): void {
        if ($event.appliedFilters.length) {
            $event.appliedFilters.forEach((filter: Filter) => {
                if (filter.field.type == 'typeahead') {
                    this.filterBy['or__' + filter.field.id] = filter.query.id;
                } else {
                    this.filterBy['or__' + filter.field.id + '__icontains'] = filter.value;
                }
            });
        } else {
            this.filterBy = {};
        }
        this.pageNumber = 1;
        this.searchRepositories();
    }

    sortChanged($event: SortEvent): void {
        if ($event.isAscending) {
            this.sortBy = $event.field.id;
        } else {
            this.sortBy = '-' + $event.field.id;
        }
        this.searchRepositories();
    }

    handlePageSizeChange($event: PaginationEvent) {
        if ($event.pageSize && this.pageSize != $event.pageSize) {
            this.pageSize = $event.pageSize;
            this.pageNumber = 1;
            this.searchRepositories();
        }
    }

    handlePageNumberChange($event: PaginationEvent) {
        if ($event.pageNumber && this.pageNumber != $event.pageNumber) {
            this.pageNumber = $event.pageNumber;
            this.searchRepositories();
        }
    }


    // private

    private searchRepositories() {
        this.pageLoading = true;
        this.filterBy['provider_namespace__namespace__name'] = this.namespace.name;
        this.filterBy['order'] = this.sortBy;
        this.filterBy['page_size'] = this.pageSize;
        this.filterBy['page'] = this.pageNumber;
        this.repositoryService.pagedQuery(this.filterBy).subscribe(
            response => {
                this.items = response.results as Repository[];
                this.prepareRepositories();
                this.filterConfig.resultsCount = response.count;
                this.paginationConfig.totalItems = response.count;
                this.pageLoading = false;
            });
    }

    private parepareNamespace() {
        // Creat an array of {'Content Type': {count: <int>, iconClass: 'icon-class'}}
        let contentCounts = [];
        for (let ct in ContentTypes) {
            if (ct == ContentTypes.plugin) {
                // summarize plugins
                let count = 0;
                let countObj = {};
                for (let count_key in this.namespace['summary_fields']['content_counts']) {
                    if (count_key.indexOf('plugin') > -1) {
                        count += this.namespace['summary_fields']['content_counts'][count_key];
                    }
                }
                if (count > 0) {
                    countObj['title'] = ContentTypesPluralChoices[ct];
                    countObj['count'] = count;
                    countObj['iconClass'] = ContentTypesIconClasses[ct];
                    contentCounts.push(countObj);
                }
            } else if (this.namespace['summary_fields']['content_counts'][ContentTypes[ct]] > 0) {
                let countObj = {}
                countObj['title'] = ContentTypesPluralChoices[ct];
                countObj['count'] = this.namespace['summary_fields']['content_counts'][ContentTypes[ct]];
                countObj['iconClass'] = ContentTypesIconClasses[ct];
                contentCounts.push(countObj);
            }
        }
        this.namespace['contentCounts'] = contentCounts;

        if (!this.namespace.avatar_url) {
            this.namespace.avatar_url = '/assets/avatar.png';
        }
    }

    private prepareRepositories() {
        this.items.forEach((item: Repository) => {
            if (!item.format) {
                item.format = 'role';
            }
            item['iconClass'] = RepoFormatsIconClasses[item.format];
            item['tooltip'] = RepoFormatsTooltips[item.format];

            item.last_import = 'NA';
            item.last_import_state = 'NA';
            if (item.summary_fields['latest_import'] && item.summary_fields['latest_import']['finished']) {
                item.last_import = moment(item.summary_fields['latest_import']['finished']).fromNow();
                item.last_import_state = item.summary_fields['latest_import']['state'];
            }

            item.last_commit = 'NA';
            if (item.commit_created) {
                item.last_commit = moment(item.commit_created).fromNow();
            }

            item.download_count = 0;
        });

    }
}
