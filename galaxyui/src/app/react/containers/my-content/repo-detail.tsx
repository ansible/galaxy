import * as React from 'react';

import { ContentToolbar } from '../../components/my-content/content-toolbar';
import { ContentType } from '../../shared-types/my-content';

export class RepoDetail extends React.Component<{}, {}> {
    render() {
        return (
            <ContentToolbar
                displayedType={ContentType.Repository}
                onSortChange={x => this.handleSortChange(x)}
                onFilterChange={x => this.handleFilterChange(x)}
            />
        );
    }

    private handleSortChange(event) {}

    private handleFilterChange(event) {}
}
