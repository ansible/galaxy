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

        const newFilters = cloneDeep(this.state.filterConfig.appliedFilters);

        if (field.type === 'select') {
            for (let i = 0; i < newFilters.length; i++) {
                if (newFilters[i].field.id === field.id) {
                    newFilters.splice(i, 1);
                }
            }
        }

        newFilters.push(newFilter);

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

    removeFilter(removed) {
        const newConfig = cloneDeep(this.state.filterConfig);

        let newValue = this.state.filterValue;
        if (removed.field.id === this.state.selectedFilter.id) {
            newValue = '';
        }

        const index = this.state.filterConfig.appliedFilters.findIndex(
            x => x.field.id === removed.field.id && x.value === removed.value,
        );

        newConfig.appliedFilters.splice(index, 1);

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
