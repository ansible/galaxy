import * as React from 'react';
import { Toolbar } from 'patternfly-react';
import { FilterPF, ToolBarResultsPF } from './patternfly-filter';
import { SortPF } from './patternfly-sort';

import { SortConfig } from '../shared-types/pf-toolbar';

import {
    FilterConfig,
    AppliedFilter,
    FilterOption,
} from '../shared-types/pf-toolbar';

import { cloneDeep } from 'lodash';

interface IProps {
    toolbarConfig: {
        filterConfig?: FilterConfig;
        sortConfig?: SortConfig;
    };
    onFilterChange?: (state) => void;
    onSortChange?: (sortEvent) => void;
}

interface IState {
    filterConfig: FilterConfig;
    selectedFilter: FilterOption;
    filterValue: string;
}

export class ToolBarPF extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);
        this.state = {
            filterConfig: this.props.toolbarConfig.filterConfig,
            selectedFilter: this.props.toolbarConfig.filterConfig.fields[0],
            filterValue: '',
        };
    }

    addFilter(value: string, field: FilterOption) {
        // // Check to see if an instance of the filter has already been added
        let alreadAdded = false;
        this.state.filterConfig.appliedFilters.forEach(i => {
            if (i.field.id === field.id) {
                if (i.value === value) {
                    alreadAdded = true;
                }
            }
        });

        if (alreadAdded) {
            return;
        }

        const newFilter = {
            field: field,
            value: value,
        } as AppliedFilter;

        const newFilters = this.state.filterConfig.appliedFilters.concat([
            newFilter,
        ]);
        const newConfig = cloneDeep(this.state.filterConfig);

        newConfig.appliedFilters = newFilters;

        this.setState(
            {
                filterConfig: newConfig,
            },
            () =>
                this.props.onFilterChange({
                    appliedFilters: this.state.filterConfig.appliedFilters,
                    field: field,
                    value: value,
                }),
        );
    }

    removeFilter(index) {
        const newConfig = cloneDeep(this.state.filterConfig);
        const removed = newConfig.appliedFilters.splice(index.index, 1);
        let newValue = this.state.filterValue;

        if (removed.field.id === this.state.selectedFilter.id) {
            newValue = '';
        }

        this.setState({ filterConfig: newConfig, filterValue: newValue }, () =>
            this.props.onFilterChange({
                appliedFilters: this.state.filterConfig.appliedFilters,
            }),
        );
    }

    removeAllFilters() {
        const newConfig = cloneDeep(this.state.filterConfig);
        newConfig.appliedFilters = [];

        this.setState({ filterConfig: newConfig }, () =>
            this.props.onFilterChange({
                appliedFilters: this.state.filterConfig.appliedFilters,
                filterValue: '',
            }),
        );
    }

    private updateFromFilter(state) {
        this.setState(state);
    }

    render() {
        return (
            <Toolbar>
                <FilterPF
                    filterConfig={this.state.filterConfig}
                    addFilter={(v, f) => this.addFilter(v, f)}
                    updateParent={state => this.updateFromFilter(state)}
                    value={this.state.filterValue}
                    field={this.state.selectedFilter}
                />
                {this.props.toolbarConfig.sortConfig ? (
                    <SortPF
                        config={this.props.toolbarConfig.sortConfig}
                        onSortChange={this.props.onSortChange}
                    />
                ) : null}

                <ToolBarResultsPF
                    numberOfResults={
                        this.props.toolbarConfig.filterConfig.resultsCount
                    }
                    appliedFilters={this.state.filterConfig.appliedFilters}
                    removeFilter={i => this.removeFilter(i)}
                    removeAllFilters={() => this.removeAllFilters()}
                />
            </Toolbar>
        );
    }
}
