import * as React from 'react';
import { Filter, FormControl, Toolbar } from 'patternfly-react';
import {
    FilterConfig,
    AppliedFilter,
    FilterOption,
    SelectorOption,
} from '../shared-types/pf-toolbar';

interface IProps {
    filterConfig: FilterConfig;
    field: FilterOption;
    value: string;
    addFilter: (value, field) => void;
    updateParent: (state) => void;
    style?: any;
}

export class FilterPF extends React.Component<IProps, {}> {
    selectFilter(filter: FilterOption) {
        this.props.updateParent({ selectedFilter: filter, filterValue: '' });
    }

    updateCurrentValue(event) {
        this.props.updateParent({ filterValue: event.target.value });
    }

    pressEnter(event) {
        if (event.key === 'Enter') {
            event.stopPropagation();
            event.preventDefault();
            if (this.props.value.length > 0) {
                this.props.addFilter(this.props.value, this.props.field);
                this.props.updateParent({ filterValue: '' });
            }
        }
    }

    filterValueSelected(option: SelectorOption) {
        this.props.addFilter(option.id, this.props.field);
        this.props.updateParent({ filterValue: option.title });
    }

    renderInput() {
        if (this.props.field.type === 'select') {
            return (
                <Filter.ValueSelector
                    filterValues={this.props.field.options}
                    currentValue={this.props.value}
                    placeholder={this.props.field.placeholder}
                    onFilterValueSelected={x => this.filterValueSelected(x)}
                />
            );
        }

        return (
            <FormControl
                type={this.props.field.type}
                placeholder={this.props.field.placeholder}
                onChange={e => this.updateCurrentValue(e)}
                value={this.props.value}
                onKeyPress={e => this.pressEnter(e)}
            />
        );
    }

    render() {
        const {
            filterConfig,
            addFilter,
            updateParent,
            value,
            field,
            ...rest
        } = this.props;
        return (
            <Filter className='form-group'>
                <Filter.TypeSelector
                    {...rest}
                    filterTypes={filterConfig.fields}
                    currentFilterType={field}
                    onFilterTypeSelected={i => this.selectFilter(i)}
                />
                {this.renderInput()}
            </Filter>
        );
    }
}

interface IResultsProps {
    appliedFilters: AppliedFilter[];
    numberOfResults: number;
    removeFilter: (index) => void;
    removeAllFilters: () => void;
}

export const ToolBarResultsPF: React.FunctionComponent<
    IResultsProps
> = props => {
    if (props.appliedFilters.length === 0) {
        return null;
    }
    return (
        <Toolbar.Results>
            <h5>{props.numberOfResults} Results</h5>
            <Filter.ActiveLabel>{'Active Filters:'}</Filter.ActiveLabel>
            <Filter.List>
                {props.appliedFilters.map((item, index) => {
                    return (
                        <Filter.Item
                            key={index}
                            filterData={{ index: index }}
                            onRemove={i =>
                                props.removeFilter(
                                    props.appliedFilters[i.index],
                                )
                            }
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
                    props.removeAllFilters();
                }}
            >
                Clear All Filters
            </a>
        </Toolbar.Results>
    );
};
