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
    numberOfResults: number;
    onSortChange: (sortEvent) => void;
    onFilterChange: (state) => void;
}

export class ContentToolbar extends React.Component<IProps, {}> {
    render() {
        const { numberOfResults } = this.props;
        const filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: 'text',
                },
                {
                    id: 'type',
                    title: 'Type',
                    placeholder: 'Filter by Collection Type...',
                    type: 'select',
                    options: [
                        { id: 'collection', title: 'Collection' },
                        { id: 'repository', title: 'Repository' },
                    ],
                },
            ] as FilterOption[],
            resultsCount: numberOfResults,
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
            <div className='toolbar'>
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
        );
    }
}
