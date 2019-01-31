import * as React from 'react';
import { PageHeader } from './page-header';

import {
    ListView,
    ListViewItem,
    EmptyState,
    EmptyStateIcon,
    EmptyStateTitle,
} from 'patternfly-react';

import { Link } from './link';
import { PagerPF } from './patternfly-pager';
import { PageLoading } from './page-loading';

import { ToolBarPF } from './patternfly-tooblar';
import { SortConfig } from './patternfly-sort';
import { FilterConfig } from './patternfly-filter';

interface ICommunityProp {
    // Configs
    headerIcon: string;
    headerTitle: string;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
    content: any;
    paginationConfig: any;
    loading: boolean;

    // Callbacks
    updateFilter: (event) => void;
    updateSort: (event) => void;
    updatePageSize: (event) => void;
    updatePageNumber: (event) => void;
}

export default class CommunityComponent extends React.Component<
    ICommunityProp,
    {}
> {
    render() {
        return (
            <div>
                <PageHeader
                    headerIcon={this.props.headerIcon}
                    headerTitle={this.props.headerTitle}
                />
                <div className='community-react-wrapper'>
                    <div id='authors-page'>
                        <div className='padding-15'>
                            <div className='row'>{this.renderToolbar()}</div>
                            <div className='row'>{this.renderList()}</div>
                            <div className='row'>{this.renderEmptyState()}</div>
                            <div className='row repository-pagination'>
                                {this.renderPagination()}
                            </div>
                        </div>
                    </div>
                </div>
                <PageLoading loading={this.props.loading} />
            </div>
        );
    }

    renderEmptyState() {
        if (this.props.content.length > 0) {
            return null;
        }
        return (
            <EmptyState>
                <EmptyStateIcon name={'pficon pficon-filter'} />
                <EmptyStateTitle>
                    No contributors match your search
                </EmptyStateTitle>
            </EmptyState>
        );
    }

    renderPagination() {
        if (this.props.content.length === 0) {
            return null;
        }
        return (
            <div className='col-sm-12'>
                <div className='pagination'>
                    <PagerPF
                        config={this.props.paginationConfig}
                        onPageSizeChange={this.props.updatePageSize}
                        onPageNumberChange={this.props.updatePageNumber}
                    />
                </div>
            </div>
        );
    }

    renderListLeft(item) {
        return (
            <div className='list-pf-left'>
                <div className='img-container'>
                    <table className='img-wrapper'>
                        <tbody>
                            <tr>
                                <td>
                                    <img src={item.avatar_url} />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }

    renderListHeader(item) {
        return (
            <Link to={'/' + item.name} className='title-link'>
                {item.name}
            </Link>
        );
    }

    renderListDescription(item) {
        return (
            <div className='list-pf-description text-overflow-pf'>
                {item.description}
            </div>
        );
    }

    renderListAdditional(item) {
        const additional = [];

        item.contentCounts.map((count, index) => {
            additional.push(
                <div key={index} className='content-count'>
                    <span className={count.iconClass} />
                    <strong>{count.count}</strong> {count.title}
                </div>,
            );
        });

        return additional;
    }

    renderList() {
        return (
            <div className='col-sm-12'>
                <div id='authors-list'>
                    <ListView>
                        {this.props.content.map((item, index) => {
                            return (
                                <ListViewItem
                                    key={index}
                                    leftContent={this.renderListLeft(item)}
                                    heading={this.renderListHeader(item)}
                                    description={this.renderListDescription(
                                        item,
                                    )}
                                    additionalInfo={this.renderListAdditional(
                                        item,
                                    )}
                                />
                            );
                        })}
                    </ListView>
                </div>
            </div>
        );
    }

    renderToolbar() {
        return (
            <div className='col-sm-12'>
                <ToolBarPF
                    onFilterChange={this.props.updateFilter}
                    onSortChange={this.props.updateSort}
                    toolbarConfig={{
                        filterConfig: this.props.filterConfig,
                        sortConfig: this.props.sortConfig,
                    }}
                />
            </div>
        );
    }
}
