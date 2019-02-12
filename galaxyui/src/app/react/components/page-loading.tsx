import * as React from 'react';

interface IProps {
    loading: boolean;
}

export class PageLoading extends React.Component<IProps, {}> {
    render() {
        // [ngClass]="{'hide-content': !loading}"
        return (
            <div className='page-loading-wrapper'>
                <div
                    className={
                        'page-loader' +
                        (this.props.loading ? '' : ' hide-content')
                    }
                >
                    <div className='page-loading-inner'>
                        <span className='fa fa-spinner fa-spin fa-5x' />
                    </div>
                </div>
            </div>
        );
    }
}
