import * as React from 'react';

import {
    FormControl,
    ListView,
    ListViewItem,
    EmptyState,
} from 'patternfly-react';

import { Namespace } from '../../../resources/namespaces/namespace';

import { Paginator } from 'patternfly-react';
import { ContentToolbar } from './content-toolbar';

interface IProps {
    itemCount: number;
    loading: boolean;
    namespace: Namespace;
    pageNumber: number;
    pageSize: number;

    setPageNumber: (x: number) => void;
    setPageSize: (x: number) => void;
    handleSortChange: (sortEvent) => void;
    handleFilterChange: (state) => void;
}

export class ContentList extends React.Component<IProps, {}> {
    render() {
        const {
            namespace,
            pageNumber,
            pageSize,
            itemCount,
            loading,
            setPageSize,
            setPageNumber,
        } = this.props;

        if (!namespace.active) {
            return (
                <EmptyState className='empty-state'>
                    <div>
                        <EmptyState.Icon name='warning-triangle-o' />
                        <EmptyState.Title>Namespace Disabled</EmptyState.Title>

                        <EmptyState.Info>
                            The Namespace {namespace.name}
                            is disabled. You'll need to re-enable it before
                            viewing and modifying its content.
                        </EmptyState.Info>
                    </div>
                </EmptyState>
            );
        }

        return (
            <div className='my-content-wrapper'>
                <ContentToolbar
                    onSortChange={x => this.props.handleSortChange(x)}
                    onFilterChange={x => this.props.handleFilterChange(x)}
                    numberOfResults={itemCount}
                />

                {itemCount > 0 ? this.props.children : this.renderEmpty()}

                {loading ? (
                    <div className='content-loader'>
                        <div className='content-loader-inner'>
                            <i className='fa fa-spinner fa-spin fa-3x' />
                        </div>
                    </div>
                ) : null}

                <Paginator
                    viewType={'list'}
                    pagination={{
                        page: pageNumber,
                        perPage: pageSize,
                        perPageOptions: [5, 10, 20, 40, 80, 100],
                    }}
                    itemCount={itemCount}
                    onPageSet={i => setPageNumber(i)}
                    onPerPageSelect={i => setPageSize(i)}
                />
            </div>
        );
    }

    renderEmpty() {
        return (
            <EmptyState className='empty-state'>
                {this.props.loading ? (
                    <span />
                ) : (
                    <div>
                        <EmptyState.Icon name='warning-triangle-o' />
                        <EmptyState.Title>No Content</EmptyState.Title>

                        <EmptyState.Info>
                            Add conent by clicking the "Add Content" button
                            above.
                        </EmptyState.Info>
                    </div>
                )}
            </EmptyState>
        );
    }
}
