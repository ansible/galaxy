import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { PageHeader } from './page-header';
import { Injector } from '@angular/core';
import { InjectorContext } from './injector-context';

import { Toolbar, ListView, ListViewItem } from 'patternfly-react';

import { Link } from './link';
import { PagerPF } from './patternfly-pager';
import { PageLoading } from './page-loading';

import { ToolBarPF } from './patternfly-tooblar';
import { SortConfig } from './patternfly-sort';
import { FilterConfig } from './patternfly-filter';

class PageConfig {
    headerIcon: string;
    headerTitle: string;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
}

interface ICommunityProp {
    config: PageConfig;
    updateFilter: (event) => void;
    updateSort: (event) => void;
    store: any;
    updatePageSize: (event) => void;
    updatePageNumber: (event) => void;
}

interface IState {
    content: any;
    paginationConfig: any;
    loading: boolean;
}

class CommunityComponent extends React.Component<ICommunityProp, IState> {
    constructor(props) {
        super(props);
        this.state = {
            loading: true,
            content: [],
            paginationConfig: {
                pageSize: 10,
                pageNumber: 1,
                totalItems: 0,
            },
        };
        this.props.store.subscribe({ next: x => this.setState(x) });
    }

    render() {
        return (
            <div>
                <PageHeader
                    headerIcon={this.props.config.headerIcon}
                    headerTitle={this.props.config.headerTitle}
                />
                <div className='community-react-wrapper'>
                    <div id='authors-page'>
                        <div className='padding-15'>
                            <div className='row'>{this.renderToolbar()}</div>
                            <div className='row'>{this.renderList()}</div>
                            <div className='row repository-pagination'>
                                {this.renderPagination()}
                            </div>
                        </div>
                    </div>
                </div>
                <PageLoading loading={this.state.loading} />
            </div>
        );
    }

    renderPagination() {
        return (
            <div className='col-sm-12'>
                <div className='pagination'>
                    <PagerPF
                        config={this.state.paginationConfig}
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
                        {this.state.content.map((item, index) => {
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
                        filterConfig: this.props.config.filterConfig,
                        sortConfig: this.props.config.sortConfig,
                    }}
                />
            </div>
        );
    }
}

export default class CommunityRenderer {
    static init(
        pageConfig,
        injector: Injector,
        updateFilter,
        updateSort,
        store,
        updatePageSize,
        updatePageNumber,
    ) {
        ReactDOM.render(
            <InjectorContext.Provider value={{ injector: injector }}>
                <CommunityComponent
                    config={pageConfig}
                    updateFilter={updateFilter}
                    updateSort={updateSort}
                    store={store}
                    updatePageSize={updatePageSize}
                    updatePageNumber={updatePageNumber}
                />
            </InjectorContext.Provider>,
            document.getElementById('react-container'),
        );
    }
}
