import * as React from 'react';
import { Toolbar } from 'patternfly-react';
import {
    FilterPF,
    FilterConfig,
    AppliedFilter,
    ToolBarResultsPF,
} from './patternfly-filter';
import { SortPF, SortConfig } from './patternfly-sort';

interface IProps {
    toolbarConfig: {
        filterConfig?: FilterConfig;
        sortConfig?: SortConfig;
    };
    onFilterChange: (state) => void;
    onSortChange: (sortEvent) => void;
}

interface IState {
    appliedFilters: AppliedFilter[];
}

export class ToolBarPF extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);
        this.state = {
            appliedFilters: this.props.toolbarConfig.filterConfig
                .appliedFilters,
        };
    }

    addFilter(value, field) {
        // // Check to see if an instance of the filter has already been added
        let alreadAdded = false;
        this.state.appliedFilters.forEach(i => {
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

        const newFilters = this.state.appliedFilters.concat([newFilter]);

        this.setState(
            {
                appliedFilters: newFilters,
            },
            () =>
                this.props.onFilterChange({
                    appliedFilters: this.state.appliedFilters,
                    field: field,
                    value: value,
                }),
        );
    }

    removeFilter(index) {
        const { appliedFilters } = this.state;
        appliedFilters.splice(index.index, 1);

        this.setState({ appliedFilters: appliedFilters }, () =>
            this.props.onFilterChange(this.state),
        );
    }

    removeAllFilters() {
        this.setState({ appliedFilters: [] }, () =>
            this.props.onFilterChange(this.state),
        );
    }

    render() {
        return (
            <Toolbar>
                <FilterPF
                    filterConfig={this.props.toolbarConfig.filterConfig}
                    addFilter={(v, f) => this.addFilter(v, f)}
                />
                <SortPF
                    config={this.props.toolbarConfig.sortConfig}
                    onSortChange={this.props.onSortChange}
                />

                <ToolBarResultsPF
                    appliedFilters={this.state.appliedFilters}
                    removeFilter={i => this.removeFilter(i)}
                    removeAllFilters={() => this.removeAllFilters()}
                />
            </Toolbar>
        );
    }
}
