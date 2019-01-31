import * as React from 'react';

import { Paginator } from 'patternfly-react';

interface IProps {
    config: PaginationConfig;
    onPageSizeChange?: (event) => void;
    onPageNumberChange?: (event) => void;
}

interface IState {
    perPage?: number;
}

export class PaginationConfig {
    pageNumber?: number;
    totalItems?: number;
    // pageSizeIncrements?: Array<number> = [5, 10, 20, 40, 80, 100];
    pageSize?: number;
}

export class PagerPF extends React.Component<IProps, {}> {
    pageSizeIncrements = [5, 10, 20, 40, 80, 100];

    onPageSet(count) {
        this.props.onPageNumberChange({ pageNumber: count });
    }

    onPerPageSelect(count) {
        this.props.onPageSizeChange({ pageSize: count });
    }

    render() {
        return (
            <Paginator
                viewType='list'
                pagination={{
                    page: this.props.config.pageNumber,
                    perPage: this.props.config.pageSize,
                    perPageOptions: this.pageSizeIncrements,
                }}
                itemCount={this.props.config.totalItems}
                onPageSet={i => this.onPageSet(i)}
                onPerPageSelect={i => this.onPerPageSelect(i)}
            />
        );
    }
}
