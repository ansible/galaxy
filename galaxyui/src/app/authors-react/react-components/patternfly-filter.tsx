import * as React from 'react';
import { Filter, FormControl, Toolbar } from 'patternfly-react';

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
    options: FilterOption[];
    onFilterChange: (appliedFilters) => void;
}

interface IState {
    currentFilter: FilterOption;
    activeFilters: AppliedFilter[];
    currentValue?: string;
}

export class FilterPF extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);

        this.state = {
            currentFilter: this.props.options[0],
            activeFilters: [],
            currentValue: '',
        };
    }

    selectFilter(filter) {
        this.setState({ currentFilter: filter });
    }

    updateCurrentValue(event) {
        this.setState({ currentValue: event.target.value });
    }

    addFilter(value) {
        // Check to see if an instance of the filter has already been added
        let alreadAdded = false;
        this.state.activeFilters.forEach(i => {
            if (i.field.id === this.state.currentFilter.id) {
                if (i.value === value) {
                    alreadAdded = true;
                }
            }
        });

        if (alreadAdded) {
            return;
        }

        const newFilters = this.state.activeFilters.concat([
            {
                field: this.state.currentFilter,
                value: value,
            } as AppliedFilter,
        ]);

        this.setState({
            activeFilters: newFilters,
        });

        this.props.onFilterChange(newFilters);
    }

    removeFilter(index) {
        const { activeFilters } = this.state;
        activeFilters.splice(index.index, 1);

        this.setState({ activeFilters: activeFilters });
    }

    clearAllFilters() {
        this.setState({ activeFilters: [] });
    }

    pressEnter(event) {
        if (event.key === 'Enter') {
            event.stopPropagation();
            event.preventDefault();
            if (this.state.currentValue.length > 0) {
                this.addFilter(this.state.currentValue);
                this.setState({ currentValue: '' });
            }
        }
    }

    renderInput() {
        return (
            <FormControl
                type={this.state.currentFilter.type}
                placeholder={this.state.currentFilter.placeholder}
                onChange={e => this.updateCurrentValue(e)}
                value={this.state.currentValue}
                onKeyPress={e => this.pressEnter(e)}
            />
        );
    }

    renderAppliedFilters() {
        if (this.state.activeFilters.length === 0) return;
        return (
            <Toolbar.Results>
                <Filter.ActiveLabel>{'Active Filters:'}</Filter.ActiveLabel>
                <Filter.List>
                    {this.state.activeFilters.map((item, index) => {
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
                        filterTypes={this.props.options}
                        currentFilterType={this.state.currentFilter}
                        onFilterTypeSelected={i => this.selectFilter(i)}
                    />
                    {this.renderInput()}
                </Filter>
                {this.renderAppliedFilters()}
            </div>
        );
    }
}
