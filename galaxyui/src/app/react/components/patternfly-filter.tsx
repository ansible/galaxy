import * as React from 'react';
import { Filter, FormControl, Toolbar } from 'patternfly-react';
import {
    FilterConfig,
    AppliedFilter,
    FilterOption,
} from '../shared-types/pf-toolbar';

interface IProps {
    filterConfig: FilterConfig;
    addFilter: (value, field) => void;
    style?: any;
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

    selectFilter(filter: FilterOption) {
        this.setState({ field: filter });
    }

    updateCurrentValue(event) {
        this.setState({ value: event.target.value });
    }

    pressEnter(event) {
        if (event.key === 'Enter') {
            event.stopPropagation();
            event.preventDefault();
            if (this.state.value.length > 0) {
                this.props.addFilter(this.state.value, this.state.field);
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

    render() {
        const { filterConfig, addFilter, ...rest } = this.props;
        return (
            <Filter className='form-group' style={{ width: '275px' }}>
                <Filter.TypeSelector
                    {...rest}
                    filterTypes={this.props.filterConfig.fields}
                    currentFilterType={this.state.field}
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
                            onRemove={i => props.removeFilter(i)}
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
