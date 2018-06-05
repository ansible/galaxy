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

import {
	Location
} from '@angular/common'

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

import {
	ContentTypes,
	ContentTypesIconClasses
} from '../enums/content-types.enum';

import {
	RepoFormats
} from '../enums/repo-types.enum';

import {
	ContributorTypes,
	ContributorTypesIconClasses
} from '../enums/contributor-types.enum';

import { PopularEvent }     from "./popular/popular.component";

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
	showRelevance: boolean = true;

	filterParams: string = '';
    sortParams: string = '&order_by=-relevance';
    sortAscending: boolean = false;
    pageSize: number = 10;
    pageNumber: number = 1;

    appliedFilters: Filter[] = [];

    constructor(
    	private route: ActivatedRoute,
    	private router: Router,
    	private contentSearch: ContentSearchService,
    	private location: Location
    ) {}

	ngOnInit() {
		this.filterConfig = {
			fields: [
				{
					id: 'keywords',
					title: 'Keyword',
					placeholder: 'Keyword',
					type: FilterType.TEXT
				},
				{
					id: 'cloud_platforms',
					title: 'Cloud Platform',
					placeholder: 'Cloud Platform',
					type: FilterType.TYPEAHEAD,
					queries: []
				},
				{
					id: 'namespaces',
					title: 'Contributor',
					placeholder: 'Name',
					type: FilterType.TEXT
				},
				{
					id: 'contributor_type',
					title: 'Contributor Type',
					placeholder: 'Contributur Type',
					type: FilterType.TYPEAHEAD,
					queries: [{
						id: ContributorTypes.community,
						value: ContributorTypes.community,
						iconStyleClass: ContributorTypesIconClasses.community
					}, {
						id: ContributorTypes.vendor,
						value: ContributorTypes.vendor,
						iconStyleClass: ContributorTypesIconClasses.vendor
					}]
				},
				{
					id: 'content_type',
					title: 'Content Type',
					placeholder: 'Content Type',
					type: FilterType.TYPEAHEAD,
					queries: []
				},
				{
					id: 'platforms',
					title: 'Platform',
					placeholder: 'Platform',
					type: FilterType.TYPEAHEAD,
        			queries: []
				},
				{
					id: 'tags',
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
			fields: [] as SortField[],
      		isAscending: true
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
            this.route.data.subscribe(
				(data) => {
					this.preparePlatforms(data.platforms);
					this.prepareContentTypes(data.contentTypes);
					this.prepareCloudPlatforms(data.cloudPlatforms);

					this.setAppliedFilters(params);
		            this.setSortConfig(params['order_by']);
		            this.setPageSize(params);

		       		this.prepareContent(data.content.results, data.content.count);
		       		this.setQuery();
					this.pageLoading = false;
				}
			);
        });
	}

	ngAfterViewInit() {}

	sortChanged($event: SortEvent): void {
		this.sortParams = '&order_by=';
		if (!$event.isAscending)
			this.sortParams += '-';
		this.sortParams += $event.field.id;
		this.searchContent();
	}

    filterChanged($event: FilterEvent): void {
    	let filterby = {}
		let params: string = '';
		this.pageNumber = 1;
		if ($event.appliedFilters.length) {
			$event.appliedFilters.forEach(filter => {
				if (filterby[filter.field.id] == undefined)
					filterby[filter.field.id] = [];
				if (filter.field.type == FilterType.TYPEAHEAD) {
					filterby[filter.field.id].push(filter.query.id);
				} else {
					filterby[filter.field.id].push(filter.value);
				}
			});
			for (var key in filterby) {
				if (params != '')
					params += '&';
				if (key == 'contributor_type') {
					if (filterby[key].length == 1) {
						switch (filterby[key][0]) {
							case ContributorTypes.community:
								params += 'vendor=false';
								break;
							case ContributorTypes.vendor:
								params += 'vendor=true';
								break
						}
					}
				} else {
					params += key + '=' + encodeURIComponent(filterby[key].join(' '));
				}
			}
			this.appliedFilters = JSON.parse(JSON.stringify($event.appliedFilters));
			this.filterParams = params;
		} else {
			this.appliedFilters = [];
			this.contentItems = [];
			this.filterParams = '';
		}
		this.searchContent();
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
				ffield = this.getFilterField('tags')
				filter = {
					field: ffield,
					value: $event.item['name']
				} as Filter;
				break;
			case 'cloudPlatforms':
				ffield = this.getFilterField('cloud_platforms');
				query = this.getFilterFieldQuery(ffield, $event.item['name'])
				filter = {
					field: ffield,
					query: query,
					value: $event.item['name']
				} as Filter;
				break;
			case 'platforms':
				ffield = this.getFilterField('platforms');
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

	itemClicked(item: Content) {
		let namespace = item.summary_fields['namespace']['name'].toLowerCase();
	    let repository = item.summary_fields['repository']['name'].toLowerCase();
		let name = item.name.toLowerCase();
		if (item['repository_format'] == RepoFormats.multi) {
			this.router.navigate(['/', namespace, repository, name]);
		} else {
			this.router.navigate(['/', namespace, repository]);
		}
	}

	// private

	private setPageSize(params:any) {
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

	private setAppliedFilters(queryParams:any) {
		// Convert query params to filters
		let filterParams = '';

        let params = JSON.parse(JSON.stringify(queryParams));
        if (!Object.keys(params).length) {
        	// When no prior query, default Contributor Type to vendor
        	params['vendor'] = true;
        }

        for (var key in params) {
        	if (key == 'vendor') {
        		var field = this.getFilterField('contributor_type');

        		if (filterParams != '')
                	filterParams += '&';
                filterParams += `vendor=${params[key]}`;

        		var ffield: Filter = {} as Filter;
        		ffield.field = field;
        		field.queries.forEach((query: FilterQuery) => {
    				if (query.id == ContributorTypes.community && !params[key]) {
    					ffield.query = query;
    					ffield.value = query.value;
    				} else if (query.id == ContributorTypes.vendor && params[key]) {
    					ffield.query = query;
    					ffield.value = query.value;
    				}
    			});
    			this.filterConfig.appliedFilters.push(ffield);
                this.appliedFilters.push(ffield);
        	} else {
	        	var field = this.getFilterField(key);
	        	if (!field)
	        		continue;

	        	if (filterParams != '')
	                filterParams += '&';
	            filterParams += `${key}=${encodeURIComponent(params[key])}`;

	        	var values: string[] = params[key].split(' ');
	        	values.forEach(v => {
	        		var ffield: Filter = {} as Filter;
	        		ffield.field = field;
	        		if (field.type == FilterType.TEXT) {
	        		  	ffield.value = v;
	        		} else if (field.type == FilterType.TYPEAHEAD) {
	        			field.queries.forEach((query: FilterQuery) => {
	        				if (query.id == v) {
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
	}

	private getBasePath(): string {
		let path = this.location.path();
		return path.replace(/\?.*$/,'');
	}

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

	private setQuery(): string {
		let paging = '&page_size=' + this.pageSize.toString() +
    		'&page=' + this.pageNumber;
    	let query = (this.filterParams + this.sortParams + paging).replace(/^&/,'');  // remove leading &
    	this.location.replaceState(this.getBasePath(), query);   // update browser URL
    	return query;
	}

    private searchContent() {
    	this.pageLoading = true;
    	let query = this.setQuery();
    	this.contentSearch.query(query)
    		.subscribe(result => {
	    		this.prepareContent(result.results, result.count);
	    		this.pageLoading = false;
    		});
    }

    private prepareContent(data: Content[], count: number) {
    	data.forEach(item => {
			item.imported = moment(item.imported).fromNow();
			item['repository_format'] = item.summary_fields['repository']['format'];
			item['avatar_url'] = item.summary_fields['namespace']['avatar_url'] || '/assets/avatar.png';
			if (!item.summary_fields['namespace']['is_vendor']) {
				// always show namespace name for community contributors
				item['namespace_name'] = item.summary_fields['namespace']['name']
			} else {
				// for vendors, assume name is in logo
				item['namespace_name'] = (item.summary_fields['namespace']['avatar_url']) ? '' : item.summary_fields['namespace']['name'];
			}
			item['displayNamespace'] = item.summary_fields['namespace']['name'];
			if (item.summary_fields['content_type']['name'].indexOf('plugin') > -1) {
				item['iconClass'] = ContentTypesIconClasses.plugin;
			} else {
				item['iconClass'] = ContentTypesIconClasses[item.summary_fields['content_type']['name']];
			}
		});
		this.contentItems = data;
		this.filterConfig.resultsCount = count;
	   	this.paginationConfig.totalItems = count;
	   	if (!count) {
	    	this.emptyStateConfig.title = this.noResultsState;
	    }
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

    private setSortConfig(orderBy?: string) {
    	let fields: SortField[] = [
    		{
		        id: 'relevance',
		        title: 'Best Match',
		        sortType: 'numeric'
		    }, {
		        id: 'namespace__name,name',
		        title: 'Contributor, Name',
		        sortType: 'alpha'
		    }, {
		        id: 'download_count',
		        title: 'Download Count',
		        sortType: 'numeric'

		    }, {
		    	id: 'repository__forks_count',
		    	title: 'Forks',
		    	sortType: 'numeric'
		    }
		    ,{
		    	id: 'repository__stargazers_count',
		    	title: 'Stars',
		    	sortType: 'numeric'
		    }, {
		    	id: 'repository__watchers_count',
		    	title: 'Watchers',
		    	sortType: 'numeric'
		    }
		] as SortField[];

    	this.sortParams = '&order_by=';
		if (this.sortConfig.isAscending)
			this.sortParams += '-';

		if (!orderBy) {
	    	// Use default order
	    	this.sortConfig.isAscending = false;
	    	this.sortConfig.fields = fields;
	    	this.sortParams += fields[0].id;
	    } else {
	    	let result: SortField[] = [] as SortField[];

	    	// Set ascending
	    	this.sortConfig.isAscending = true;
	    	if (orderBy.startsWith('-')) {
	    		this.sortConfig.isAscending = false;
	    	}

	    	// Put the requested orderby field at the top of the list
	    	let order = orderBy.replace(/^[+-]/, '');
	    	fields.forEach(f => {
	    		if (f.id == order) {
	    			result.push(f);
	    			this.sortParams += f.id;
	    		}
	    	})
	    	fields.forEach(f => {
	    		if (f.id != order) {
	    			result.push(f);
	    		}
	    	});
	    	this.sortConfig.fields =result;
	    }
    }
}
