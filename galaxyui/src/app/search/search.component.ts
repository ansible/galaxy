import {
	Component,
	OnInit,
	ViewChild,
	AfterViewInit
} from '@angular/core';

import {
	ActivatedRoute,
	Router
} from '@angular/router';

import { ListConfig }     from 'patternfly-ng/list/basic-list/list-config';
import { ListEvent }      from 'patternfly-ng/list/list-event';
import { ListComponent }  from 'patternfly-ng/list/basic-list/list.component';

import { ToolbarView }    from "patternfly-ng/toolbar/toolbar-view";
import { ToolbarConfig }  from "patternfly-ng/toolbar/toolbar-config";

import { FilterConfig }   from "patternfly-ng/filter/filter-config";
import { Filter }         from "patternfly-ng/filter/filter";
import { FilterField }    from "patternfly-ng/filter/filter-field";
import { FilterEvent }    from "patternfly-ng/filter/filter-event";
import { FilterQuery }    from 'patternfly-ng/filter/filter-query';
import { FilterType }     from "patternfly-ng/filter/filter-type";

import { SortConfig }     from "patternfly-ng/sort/sort-config";
import { SortField }      from "patternfly-ng/sort/sort-field";
import { SortEvent }      from "patternfly-ng/sort/sort-event";

import { PaginationConfig }     from 'patternfly-ng/pagination/pagination-config';
import { PaginationEvent }      from 'patternfly-ng/pagination/pagination-event';

import { EmptyStateConfig }     from "patternfly-ng/empty-state/empty-state-config";

import { ContentSearchService } from "../resources/content-search/content-search.service";
import { Platform }             from "../resources/platforms/platform";
import { ContentType }          from "../resources/content-types/content-type";
import { CloudPlatform }        from "../resources/cloud-platforms/cloud-platform";

import { PopularEvent }   from "./popular/popular.component";

import {
	Content,
	ContentResponse
} from "../resources/content-search/content";

import * as moment        from 'moment';

@Component({
    selector: 'app-search',
    templateUrl: './search.component.html',
    styleUrls: ['./search.component.less']
})
export class SearchComponent implements OnInit, AfterViewInit {

	pageTitle: string = "Search";
	toolbarConfig: ToolbarConfig;
	filterConfig: FilterConfig;
	sortConfig: SortConfig;
	contentItems: Content[];
	listConfig: ListConfig;
	paginationConfig: PaginationConfig;
	
	emptyStateConfig: EmptyStateConfig;
	defaultEmptyStateTitle: string;
	noResultsState: string = 'No matching results found';

	pageLoading: boolean = true;
	showRelevance: boolean = false;
	
	filterParams: string;
    sortParams: string = '&order_by=-relevance';
    sortAscending: boolean = false;
    pageSize: number = 10;
    pageNumber: number = 1;

    appliedFilters: Filter[] = [];

    constructor(
    	private route: ActivatedRoute,
    	private contentSearch: ContentSearchService
    ) {}

	ngOnInit() {
		this.filterConfig = {
			fields: [
				{
					id: 'keyword',
					title: 'Keyword',
					placeholder: 'Keyword',
					type: FilterType.TEXT
				},
				{ 
					id: 'cloud_platform',
					title: 'Cloud Platform',
					placeholder: 'Cloud Platform',
					type: FilterType.TYPEAHEAD,
					queries: []
				},
				{
					id: 'content_type',
					title: 'Content Type',
					placeholder: 'Content Type',
					type: FilterType.TYPEAHEAD,
					queries: []
				},
				{
					id: 'namespace',
					title: 'Namespace',
					placeholder: 'Namespace',
					type: FilterType.TEXT
				},
				{
					id: 'platform',
					title: 'Platform',
					placeholder: 'Platform',
					type: FilterType.TYPEAHEAD,
        			queries: []
				},
				{
					id: 'tag',
					title: 'Tag',
					placeholder: 'Tag',
					type: FilterType.TEXT
				}
			] as FilterField[],
			resultsCount: 0,
			totalCount: 0,
			appliedFilters: []
		} as FilterConfig;

		this.sortConfig = {
			fields: [{
		        id: 'relevance',
		        title: 'Best Match',
		        sortType: 'numeric'
		    }, {
		        id: 'download_count',
		        title: 'Download Count',
		        sortType: 'numeric'
		    
		    }, {
		        id: 'name',
		        title: 'Namespace, Name',
		        sortType: 'alpha'
		    }, {
		    	id: 'stargazers',
		    	title: 'Star Gazers',
		    	sortType: 'numeric'
		    }, {
		    	id: 'watchers',
		    	title: 'Watchers',
		    	sortType: 'numeric'
		    }],
      		isAscending: this.sortAscending
		} as SortConfig;

		this.emptyStateConfig = {
			info: '',
			title: this.noResultsState,
			iconStyleClass: 'pficon pficon-filter'
		} as EmptyStateConfig;

		this.toolbarConfig = {
			filterConfig: this.filterConfig,
			sortConfig: this.sortConfig
		} as ToolbarConfig;

		this.listConfig = {
			emptyStateConfig: this.emptyStateConfig
		} as ListConfig;

		this.paginationConfig = {
	        pageSize: 10,
	        pageNumber: 1,
	        totalItems: 0
	    } as PaginationConfig;

	    this.route.queryParams.subscribe(params => {
            if (params['keywords']) {
            	console.log(params['keywords']);
            	let keywords: string[] = params['keywords'].split(' ');
            	keywords.forEach(kw => {
            		let ffield: Filter = {
	                	field: this.getFilterField('keyword'),
	                	value: kw
		            }
	            	this.filterConfig.appliedFilters.push(ffield);
	                this.appliedFilters.push(ffield);	
            	});
            }

            this.route.data.subscribe(
				(data) => {
					let count = data.content.count.toString().replace(/(\d)(?=(\d{3})$)/g, '$1,');
					this.preparePlatforms(data.platforms);
					this.prepareContentTypes(data.contentTypes);
					this.prepareCloudPlatforms(data.cloudPlatforms);
					this.defaultEmptyStateTitle = `Search our index of ${count} Ansible content items.`;
					this.emptyStateConfig.title = this.defaultEmptyStateTitle;
					this.pageLoading = false;
					
					if (this.appliedFilters.length) {
						// keywords passed in from Home page, so trigger a search
						let event = new FilterEvent();
						event.appliedFilters = JSON.parse(JSON.stringify(this.appliedFilters)) as Filter[];
						this.filterChanged(event);
					}
				}
			);
        });
	}

	ngAfterViewInit() {}

	sortChanged($event: SortEvent): void {
		this.sortAscending = $event.isAscending;
		this.sortParams = '&order_by=';
		let params = '';
		if (!this.sortAscending)
			this.sortParams += '-';
		switch ($event.field.id) {
			case 'download_count':
				this.sortParams += 'download_count';
				break;
			case 'relevance':
				this.sortParams += 'relevance'
				break;
			case 'name':
				this.sortParams += 'namespace__name,name'
				break;
			case 'stargazers':
				this.sortParams += 'repository__stargazers_count'
				break;
			case 'watchers':
				this.sortParams += 'repository__watchers_count'
				break;
		}
		if (this.filterParams) {
			this.showRelevance = true;
			this.searchContent();
		}
	}

    filterChanged($event: FilterEvent): void {
    	let filterby = {}
		let params: string = '';
		this.pageNumber = 1;
		if ($event.appliedFilters.length) {
			$event.appliedFilters.forEach(filter => {
				if (filterby[filter.field.id] == undefined)
					filterby[filter.field.id] = [];
				if (filter.field.type == 'typeahead') {
					filterby[filter.field.id].push(filter.query.id);
				} else {
					filterby[filter.field.id].push(filter.value);
				}
			});
			for (var key in filterby) {
				if (params != '')
					params += '&';
				if (key == 'content_type') {
					// contenty_type only accepts a single value
					params += key + '=' + encodeURIComponent(filterby[key][0]); 
				} else {
					params += key + 's=' + encodeURIComponent(filterby[key].join(' '));		
				}
			}
			this.appliedFilters = JSON.parse(JSON.stringify($event.appliedFilters));
			this.showRelevance = true;
			this.filterParams = params;
			this.searchContent();
		} else {
			this.appliedFilters = [];
			this.showRelevance = false;
			this.contentItems = [];
			this.filterParams = null;
			this.emptyStateConfig.title = this.defaultEmptyStateTitle;
		}
	}

	getToolbarConfig() :ToolbarConfig {
		this.toolbarConfig.filterConfig.appliedFilters = JSON.parse(JSON.stringify(this.appliedFilters));
		return this.toolbarConfig;	
	}

	handlePageSizeChange($event: PaginationEvent) {
		if ($event.pageSize && this.pageSize != $event.pageSize) {
			this.pageSize = $event.pageSize;
			this.pageNumber = 1;
			this.searchContent();
		}
	}

	handlePageNumberChange($event: PaginationEvent) {
		if ($event.pageNumber && this.pageNumber != $event.pageNumber) {
			this.pageNumber = $event.pageNumber;
			this.searchContent();
		}
	}

	handleWidgetClick($event: PopularEvent) {
		let filter: Filter;
		let ffield: FilterField;
		let query: FilterQuery;
		let event: FilterEvent;
		switch ($event.itemType) {
			case 'tags':
				ffield = this.getFilterField('tag')
				filter = {
					field: ffield,
					value: $event.item['name']
				} as Filter;
				break;
			case 'cloudPlatforms':
				ffield = this.getFilterField('cloud_platform');
				query = this.getFilterFieldQuery(ffield, $event.item['name'])
				filter = {
					field: ffield,
					query: query,
					value: $event.item['name']
				} as Filter;
				break;
			case 'platforms':
				ffield = this.getFilterField('platform');
				query = this.getFilterFieldQuery(ffield, $event.item['name'])
				filter = {
					field: ffield,
					query: query,
					value: $event.item['name']
				} as Filter;
				break;
		}
		if (filter) {
			// Update applied filters, and refresh the search result
			this.addToFilter(filter);
			event = new FilterEvent();
			event.appliedFilters = JSON.parse(JSON.stringify(this.appliedFilters)) as Filter[];
			event.field = JSON.parse(JSON.stringify(ffield)) as FilterField;
			if (query)
				event.query = JSON.parse(JSON.stringify(query)) as FilterQuery;
			event.value = $event.item['name'];
			this.filterChanged(event);
		}
	}

	// private
    
	private getFilterField(id: string): FilterField {
		let result: FilterField = null;
		this.filterConfig.fields.forEach((item: FilterField) => {
			if (item.id == id) {
				result = item;
			}
		})
		return result;
	}

	private getFilterFieldQuery(field: FilterField, value: string): FilterQuery {
		let result: FilterQuery = null;
		field.queries.forEach((item: FilterQuery) => {
			if (item.value == value) {
				result = item;
			}
		});
		return result;
	}

	private addToFilter(filter: Filter) {
		let filterExists: boolean = false;
		this.appliedFilters.forEach( (item: Filter) => {
			if (item.field.id == filter.field.id && item.value == filter.value) {
				filterExists = true;
			}
		});
		if (!filterExists) {
			this.appliedFilters.push(JSON.parse(JSON.stringify(filter)));
		}
	}

    private searchContent(params?: string) {
    	this.pageLoading = true;
    	let paging = '&page_size=' + this.pageSize.toString() +
    		'&page=' + this.pageNumber;
    	let query = this.filterParams + this.sortParams + paging;
    	this.contentSearch.query(query)
    		.subscribe(result => {
	    		result.results.forEach(item => {
	    			item.imported = moment(item.imported).fromNow();
	    		});
	    		this.contentItems = result.results;
	    		this.filterConfig.resultsCount = result.count;
	    		this.pageLoading = false;
	    		this.paginationConfig.totalItems = result.count;
	    		if (!result.count) {
	    			this.emptyStateConfig.title = this.noResultsState;
	    		}
    		});
    }

    private getFilterConfigFieldIdx(id: string): number {
    	let result = null;
		this.filterConfig.fields.forEach((fld: SortField, idx: number) => {
			if (fld.id == id) {
				result = idx;
			}
		});
		return result;
    }

    private preparePlatforms(platforms: Platform[]): void {
    	// Add Platforms to filterConfig
    	let idx = this.getFilterConfigFieldIdx('platform');
		if (idx !== null) {
	    	let platformMap = {};
	    	platforms.forEach(platform => {
	    		platformMap[platform.name] = true;
	    	});
	    	this.toolbarConfig.filterConfig.fields[idx].queries = []
	    	for (var key in platformMap) {
	    		this.toolbarConfig.filterConfig.fields[idx].queries.push({
	    			id: key,
	    			value: key
	    		});
	    	}
	    }
    }

    private prepareContentTypes(contentTypes: ContentType[]): void {
    	// Add Content Types to filterConfig
    	let idx = this.getFilterConfigFieldIdx('content_type');
    	if (idx !== null) {
	    	let contentTypeMap = {};
	    	contentTypes.forEach(ct => {
	    		contentTypeMap[ct.name] = ct.description;
	    	});
	    	this.toolbarConfig.filterConfig.fields[idx].queries = []
	    	for (var key in contentTypeMap) {
	    		this.toolbarConfig.filterConfig.fields[idx].queries.push({
	    			id: key,
	    			value: contentTypeMap[key]
	    		});
	    	}
	    }
    }

    private prepareCloudPlatforms(contentTypes: CloudPlatform[]): void {
    	// Add Cloud Platforms to filterConfig
    	let idx = this.getFilterConfigFieldIdx('cloud_platform');
		if (idx !== null) {
	    	let cpMap = {};
	    	contentTypes.forEach(cp => {
	    		cpMap[cp.name] = cp.description;
	    	});
	    	this.toolbarConfig.filterConfig.fields[idx].queries = []
	    	for (var key in cpMap) {
	    		this.toolbarConfig.filterConfig.fields[idx].queries.push({
	    			id: key,
	    			value: cpMap[key]
	    		});
	    	}
	    }
    }
}
