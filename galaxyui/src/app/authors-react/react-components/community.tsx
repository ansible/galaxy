import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { PageHeader } from './page-header';
import { Injector } from '@angular/core';
import { InjectorContext } from './injector-context';

import { Toolbar, ListView, ListViewItem } from 'patternfly-react';

import { FilterPF, FilterConfig } from './patternfly-filter';
import { SortPF, SortConfig } from './patternfly-sort';
import { Link } from './link';

class PageConfig {
    headerIcon: string;
    headerTitle: string;
    filterConfig: FilterConfig;
    sortConfig: SortConfig;
}

interface ICommunityProp {
    config: PageConfig;
    updateFilter?: (event) => void;
    updateSort?: (event) => void;
    updatePage?: (event) => void;
    updateContent?: (data) => void;
    store?: any;
}

interface IState {
    content: any;
}

class CommunityComponent extends React.Component<ICommunityProp, IState> {
    constructor(props) {
        super(props);
        this.state = { content: [] };
        this.props.store.subscribe({ next: x => this.updateContent(x) });
    }

    updateContent(newContent) {
        this.setState({ content: newContent });
    }

    render() {
        return [
            <PageHeader
                key={1}
                headerIcon={this.props.config.headerIcon}
                headerTitle={this.props.config.headerTitle}
            />,
            <div key={2} className='community-react-wrapper'>
                <div id='authors-page'>
                    <div className='padding-15'>
                        <div className='row'>{this.renderToolbar()}</div>
                        <div className='row'>{this.renderList()}</div>
                    </div>
                </div>
            </div>,
        ];
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
                <Toolbar>
                    <FilterPF
                        filterConfig={this.props.config.filterConfig}
                        onFilterChange={this.props.updateFilter}
                    />
                    <SortPF
                        onSortChange={this.props.updateSort}
                        config={this.props.config.sortConfig}
                    />
                </Toolbar>
            </div>
        );
    }
}

//
//     <div class="row repository-pagination">
//         <div class="col-sm-12">
//             <div class="pagination" *ngIf="items && items.length && paginationConfig.totalItems > paginationConfig.pageSize">
//                 <pfng-pagination
//                     [config]="paginationConfig"
//                     (onPageSizeChange)="handlePageSizeChange($event)"
//                     (onPageNumberChange)="handlePageNumberChange($event)">
//                 </pfng-pagination>
//             </div>
//         </div>
//     </div>
//
// </div>

export default class CommunityRenderer {
    static init(
        pageConfig,
        injector: Injector,
        updateFilter,
        updateSort,
        store,
    ) {
        ReactDOM.render(
            <InjectorContext.Provider value={{ injector: injector }}>
                <CommunityComponent
                    config={pageConfig}
                    updateFilter={updateFilter}
                    updateSort={updateSort}
                    store={store}
                />
            </InjectorContext.Provider>,
            document.getElementById('react-container'),
        );
    }
}
