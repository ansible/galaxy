import * as React from 'react';

import { Sort } from 'patternfly-react';

class FieldOption {
    id: string;
    title: string;
    sortType: string;
}

export class SortConfig {
    fields: FieldOption[];
    isAscending: boolean;
}

interface IProps {
    config: SortConfig;
    onSortChange: (sortEvent) => void;
}

interface IState {
    isAscending: boolean;
    activeOption: FieldOption;
}

export class SortPF extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);

        this.state = {
            isAscending: this.props.config.isAscending,
            activeOption: this.props.config.fields[0],
        };
    }

    updateSortType(sortType) {
        this.setState({ activeOption: sortType });
        this.props.onSortChange({
            field: sortType,
            isAscending: this.state.isAscending,
        });
    }

    toggleSortDirection() {
        const sortDir = !this.state.isAscending;

        this.setState({ isAscending: sortDir });
        this.props.onSortChange({
            field: this.state.activeOption,
            isAscending: sortDir,
        });
    }

    render() {
        return (
            <Sort>
                <Sort.TypeSelector
                    sortTypes={this.props.config.fields}
                    currentSortType={this.state.activeOption}
                    onSortTypeSelected={i => this.updateSortType(i)}
                />
                <Sort.DirectionSelector
                    isAscending={this.state.isAscending}
                    isNumeric={this.state.activeOption.sortType === 'numeric'}
                    onClick={_ => this.toggleSortDirection()}
                />
            </Sort>
        );
    }
}
