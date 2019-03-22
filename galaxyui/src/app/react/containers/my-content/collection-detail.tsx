import * as React from 'react';

import { ContentToolbar } from '../../components/my-content/content-toolbar';
import { ContentType } from '../../shared-types/my-content';

interface IProps {
    displayedType: ContentType;
    setDisplayedType: (x: ContentType) => void;
}

export class CollectionDetail extends React.Component<IProps, {}> {
    render() {
        return (
            <div className='my-content-wrapper'>
                <ContentToolbar
                    displayedType={this.props.displayedType}
                    onSortChange={x => this.handleSortChange(x)}
                    onFilterChange={x => this.handleFilterChange(x)}
                    setDisplayedType={this.props.setDisplayedType}
                    numberOfResults={0}
                />
                OOooooooh weee. I'm a CooOOllection!
            </div>
        );
    }

    private handleSortChange(event) {}

    private handleFilterChange(event) {}
}
