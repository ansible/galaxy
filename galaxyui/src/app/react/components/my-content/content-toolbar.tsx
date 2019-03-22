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
    numberOfResults: number;

    onSortChange: (sortEvent) => void;
    onFilterChange: (state) => void;
    setDisplayedType: (contentType: ContentType) => void;
}

export class ContentToolbar extends React.Component<IProps, {}> {
    render() {
        const { displayedType, numberOfResults } = this.props;
        const filterConfig = {
            fields: [
                {
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by Name...',
                    type: 'text',
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
                <div className='content-toggle'>
                    <a
                        className={
                            displayedType === ContentType.Collection
                                ? 'btn btn-primary'
                                : 'btn'
                        }
                        onClick={() =>
                            this.props.setDisplayedType(ContentType.Collection)
                        }
                    >
                        Collections
                    </a>
                    <a
                        className={
                            displayedType === ContentType.Repository
                                ? 'btn btn-primary'
                                : 'btn'
                        }
                        onClick={() =>
                            this.props.setDisplayedType(ContentType.Repository)
                        }
                    >
                        Repositories
                    </a>
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
        );
    }
}
