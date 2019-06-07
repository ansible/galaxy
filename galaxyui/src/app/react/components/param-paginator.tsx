import * as React from 'react';
import { ParamHelper } from '../lib/param-helper';
import { Paginator } from 'patternfly-react';

interface IProps {
    params: Object;
    count: number;
    pageNumberParam?: string;
    pageSizeParam?: string;

    updateParams: (params) => void;
}

export class ParamPaginator extends React.Component<IProps, {}> {
    static defaultProps = {
        pageNumberParam: 'page',
        pageSizeParam: 'page_size',
    };

    render() {
        const { params, count, pageNumberParam, pageSizeParam } = this.props;
        const page = params[pageNumberParam] || 1;
        const perPage = params[pageSizeParam] || 10;
        return (
            <Paginator
                viewType={'list'}
                pagination={{
                    page: page,
                    perPage: perPage,
                    perPageOptions: [10, 20, 40, 80, 100],
                }}
                itemCount={count}
                onPageSet={i => this.setPageNumber(i)}
                onPerPageSelect={i => this.setPageSize(i)}
            />
        );
    }

    private setPageSize(size) {
        let params = ParamHelper.setParam(
            this.props.params,
            this.props.pageSizeParam,
            size,
        );

        params = ParamHelper.setParam(params, this.props.pageNumberParam, 1);

        this.props.updateParams(params);
    }

    private setPageNumber(pageNum) {
        this.props.updateParams(
            ParamHelper.setParam(
                this.props.params,
                this.props.pageNumberParam,
                pageNum,
            ),
        );
    }
}
