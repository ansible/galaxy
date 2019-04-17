// Used to configure Filters for the pattenfly toolbar and patternfly filter
export class FilterConfig {
    resultsCount: number;
    fields: FilterOption[];
    appliedFilters: AppliedFilter[];
}

// Options in the dropdown menu for the patternfly filter
export class FilterOption {
    id: string;
    title: string;
    placeholder: string;
    type: string;
    options?: SelectorOption[];
}

// Filters that have been added to a particular query (these are the little
// blue boxes that appear underneath the filter)
export class AppliedFilter {
    field: FilterOption;
    query?: string;
    value: string;
}

// Configuration for sort widget on patternfly toolbar
export class SortConfig {
    fields: SortFieldOption[];
    isAscending: boolean;
}

// List of options in sort dropdown menu in the sort widget
export class SortFieldOption {
    id: string;
    title: string;
    sortType: string;
}

// List of options for filter dropdown menu when type: select is sepcified in
// the FilterOption
export class SelectorOption {
    id: string;
    title: string;
}
