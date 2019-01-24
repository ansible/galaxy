import * as React from 'react';

import { Paginator } from 'patternfly-react';

interface IProps {
    config: PaginationConfig;
    onPageSizeChange?: (event) => void;
    onPageNumberChange?: (event) => void;
}

interface IState {
    page?: number;
    perPage?: number;
}

class PaginationConfig {
    pageNumber?: number;
    totalItems?: number;
    // pageSizeIncrements?: Array<number> = [5, 10, 20, 40, 80, 100];
    pageSize?: number;
}

export class PagerPF extends React.Component<IProps, IState> {
    pageSizeIncrements = [5, 10, 20, 40, 80, 100];

    constructor(props) {
        super(props);
        this.state = {
            page: this.props.config.pageNumber,
            perPage: this.props.config.pageSize,
        };

        // if (this.props.config.pageSizeIncrements === undefined) {
        //     this.props.config.pageSizeIncrements = [5, 10, 20, 40, 80, 100];
        // }
    }

    onPageSet(count) {
        this.setState({ page: count }, () =>
            this.props.onPageNumberChange({ pageNumber: this.state.page }),
        );
    }

    onPerPageSelect(count) {
        this.setState({ perPage: count }, () =>
            this.props.onPageSizeChange({ pageSize: this.state.perPage }),
        );
    }

    render() {
        return (
            <Paginator
                viewType='list'
                pagination={{
                    page: this.state.page,
                    perPage: this.state.perPage,
                    perPageOptions: this.pageSizeIncrements,
                }}
                itemCount={this.props.config.totalItems}
                onPageSet={i => this.onPageSet(i)}
                onPerPageSelect={i => this.onPerPageSelect(i)}
            />
        );
    }
}
