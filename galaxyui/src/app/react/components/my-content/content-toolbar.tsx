import * as React from 'react';
import { ToolBarPF } from '../patternfly-toolbar';
import {
    SortConfig,
    FilterConfig,
    FilterOption,
    AppliedFilter,
    SortFieldOption,
} from '../../shared-types/pf-toolbar';

import { ContentType } from '../../shared-types/my-content';

interface IProps {
    displayedType: ContentType;

    onSortChange: (sortEvent) => void;
    onFilterChange: (state) => void;
}

export class ContentToolbar extends React.Component<IProps, {}> {
    render() {
        const filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: 'text',
                },
            ] as FilterOption[],
            resultsCount: 0,
            appliedFilters: [] as AppliedFilter[],
        } as FilterConfig;

        const sortConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    sortType: 'alpha',
                },
                {
                    id: 'modified',
                    title: 'Last Modified',
                    sortType: 'alpha',
                },
            ] as SortFieldOption[],
            isAscending: true,
        } as SortConfig;

        return (
            <div className='my-content-wrapper'>
                <div className='toolbar'>
                    <div className='content-toggle'>
                        <a className='btn'>Collections</a>
                        <a className='btn btn-primary'>Repositories</a>
                    </div>
                    &nbsp; &nbsp; &nbsp; &nbsp;
                    <div>
                        <ToolBarPF
                            toolbarConfig={{
                                filterConfig: filterConfig,
                                sortConfig: sortConfig,
                            }}
                            onFilterChange={this.props.onFilterChange}
                            onSortChange={this.props.onSortChange}
                        />
                    </div>
                </div>
            </div>
        );
    }
}
