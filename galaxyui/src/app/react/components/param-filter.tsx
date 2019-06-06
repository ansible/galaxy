import * as React from 'react';
import { Toolbar } from 'patternfly-react';
import { FilterPF, ToolBarResultsPF } from './patternfly-filter';
import { SortPF } from './patternfly-sort';
import { ParamHelper } from '../lib/param-helper';

import { SortConfig } from '../shared-types/pf-toolbar';

import {
    FilterConfig,
    AppliedFilter,
    FilterOption,
    SortFieldOption,
} from '../shared-types/pf-toolbar';

import { cloneDeep } from 'lodash';

interface IProps {
    filterFields?: FilterOption[];
    sortFields?: SortFieldOption[];
    params: Object;
    count: number;
    orderParam: string;
    updateParams: (params) => void;
}

interface IState {
    selectedFilter: FilterOption;
    filterValue: string;
}

export class ToolBarPF extends React.Component<IProps, IState> {
    static defaultProps;
    constructor(props) {
        super(props);
        this.state = {
            // filterConfig: this.props.toolbarConfig.filterConfig,
            selectedFilter: this.props.filterFields[0],
            filterValue: '',
        };
    }

    private addFilter(value: string, field: FilterOption) {
        // Check to see if an instance of the filter has already been added
        if (ParamHelper.paramExists(this.props.params, field.id, value)) {
            return;
        }

        if (field.type === 'typeahead') {
            this.props.updateParams(
                ParamHelper.appendParam(this.props.params, field.id, value),
            );
        } else {
            this.props.updateParams(
                ParamHelper.setParam(this.props.params, field.id, value),
            );
        }
    }

    private removeFilter(filter: AppliedFilter) {
        this.props.updateParams(
            ParamHelper.deleteParam(
                this.props.params,
                filter.field.id,
                filter.value,
            ),
        );
    }

    private removeAllFilters() {
        const params = cloneDeep(this.props.params);
        for (const field of this.props.filterFields) {
            delete params[field.id];
        }

        this.props.updateParams(params);
    }

    private updateFromFilter(state) {
        this.setState(state);
    }

    private paramsToAppliedFilters(params) {
        const appliedFilters = [] as AppliedFilter[];

        for (const field of this.props.filterFields) {
            const val = params[field.id];
            if (val) {
                if (Array.isArray(val)) {
                    for (const v of val) {
                        appliedFilters.push({
                            field: field,
                            value: v,
                        });
                    }
                } else {
                    appliedFilters.push({
                        field: field,
                        value: val,
                    });
                }
            }
        }

        return appliedFilters;
    }

    private getIsAscending(params) {
        // if sort starts with '-', isAscending = false
        const sort = params[this.props.orderParam];
        if (sort) {
            return !sort.startsWith('-');
        } else {
            return true;
        }
    }

    private onSortChange($event) {
        let sortVal = '';
        if ($event.isAscending) {
            sortVal = $event.field.id;
        } else {
            sortVal = '-' + $event.field.id;
        }

        this.props.updateParams(
            ParamHelper.setParam(
                this.props.params,
                this.props.orderParam,
                sortVal,
            ),
        );
    }

    render() {
        const { count, filterFields, sortFields, params } = this.props;

        // Derive the child configurations from the params object
        const appliedFilters = this.paramsToAppliedFilters(params);

        let filterConfig = null;
        if (filterFields) {
            filterConfig = {
                resultsCount: count,
                fields: filterFields,
                appliedFilters: appliedFilters,
            } as FilterConfig;
        }

        let sortConfig = null;
        if (sortFields) {
            sortConfig = {
                fields: sortFields,
                isAscending: this.getIsAscending(params),
            } as SortConfig;
        }

        return (
            <Toolbar>
                {filterConfig ? (
                    <FilterPF
                        filterConfig={filterConfig}
                        addFilter={(v, f) => this.addFilter(v, f)}
                        updateParent={state => this.updateFromFilter(state)}
                        value={this.state.filterValue}
                        field={this.state.selectedFilter}
                    />
                ) : null}

                {sortConfig ? (
                    <SortPF
                        config={sortConfig}
                        onSortChange={x => this.onSortChange(x)}
                    />
                ) : null}

                <ToolBarResultsPF
                    numberOfResults={count}
                    appliedFilters={appliedFilters}
                    removeFilter={i => this.removeFilter(i)}
                    removeAllFilters={() => this.removeAllFilters()}
                />
            </Toolbar>
        );
    }
}
