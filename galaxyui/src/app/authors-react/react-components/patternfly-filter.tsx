import * as React from 'react';
import { Filter, FormControl, Toolbar } from 'patternfly-react';

export class FilterConfig {
    resultsCount: number;
    fields: FilterOption[];
    appliedFilters: AppliedFilter[];
}

export class FilterOption {
    id: string;
    title: string;
    placeholder: string;
    type: string;
}

class AppliedFilter {
    field: FilterOption;
    query?: string;
    value: string;
}

interface IProps {
    filterConfig: FilterConfig;
    onFilterChange: (state) => void;
}

interface IState {
    field: FilterOption;
    appliedFilters: AppliedFilter[];
    value?: string;
}

export class FilterPF extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);

        this.state = {
            field: this.props.filterConfig.fields[0],
            appliedFilters: this.props.filterConfig.appliedFilters,
            value: '',
        };
    }

    selectFilter(filter) {
        this.setState({ field: filter });
    }

    updateCurrentValue(event) {
        this.setState({ value: event.target.value });
    }

    emitState() {}

    addFilter(value) {
        // Check to see if an instance of the filter has already been added
        let alreadAdded = false;
        this.state.appliedFilters.forEach(i => {
            if (i.field.id === this.state.field.id) {
                if (i.value === value) {
                    alreadAdded = true;
                }
            }
        });

        if (alreadAdded) {
            return;
        }

        const newFilter = {
            field: this.state.field,
            value: value,
        } as AppliedFilter;

        const newFilters = this.state.appliedFilters.concat([newFilter]);

        this.setState(
            {
                appliedFilters: newFilters,
            },
            () => this.props.onFilterChange(this.state),
        );
    }

    removeFilter(index) {
        const { appliedFilters } = this.state;
        appliedFilters.splice(index.index, 1);

        this.setState({ appliedFilters: appliedFilters }, () =>
            this.props.onFilterChange(this.state),
        );
    }

    clearAllFilters() {
        this.setState({ appliedFilters: [] }, () =>
            this.props.onFilterChange(this.state),
        );
    }

    pressEnter(event) {
        if (event.key === 'Enter') {
            event.stopPropagation();
            event.preventDefault();
            if (this.state.value.length > 0) {
                this.addFilter(this.state.value);
                this.setState({ value: '' });
            }
        }
    }

    renderInput() {
        return (
            <FormControl
                type={this.state.field.type}
                placeholder={this.state.field.placeholder}
                onChange={e => this.updateCurrentValue(e)}
                value={this.state.value}
                onKeyPress={e => this.pressEnter(e)}
            />
        );
    }

    renderAppliedFilters() {
        if (this.state.appliedFilters.length === 0) return;
        return (
            <Toolbar.Results>
                <Filter.ActiveLabel>{'Active Filters:'}</Filter.ActiveLabel>
                <Filter.List>
                    {this.state.appliedFilters.map((item, index) => {
                        return (
                            <Filter.Item
                                key={index}
                                filterData={{ index: index }}
                                onRemove={i => this.removeFilter(i)}
                            >
                                {item.field.title}: {item.value}
                            </Filter.Item>
                        );
                    })}
                </Filter.List>
                <a
                    href='#'
                    onClick={e => {
                        e.preventDefault();
                        this.clearAllFilters();
                    }}
                >
                    Clear All Filters
                </a>
            </Toolbar.Results>
        );
    }

    render() {
        return (
            <div>
                <Filter>
                    <Filter.TypeSelector
                        filterTypes={this.props.filterConfig.fields}
                        currentFilterType={this.state.field}
                        onFilterTypeSelected={i => this.selectFilter(i)}
                    />
                    {this.renderInput()}
                </Filter>
                {this.renderAppliedFilters()}
            </div>
        );
    }
}
