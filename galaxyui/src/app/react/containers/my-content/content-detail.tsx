import { Namespace } from '../../../resources/namespaces/namespace';
import { Injector } from '@angular/core';

import * as React from 'react';
import { ContentType } from '../../shared-types/my-content';
import { RepoDetail } from './repo-detail';
import { CollectionDetail } from './collection-detail';

interface IProps {
    namespace: Namespace;
    injector: Injector;
}

interface IState {
    displayedContent: ContentType;
}

export class ContentDetailContainer extends React.Component<IProps, IState> {
    constructor(props) {
        super(props);

        this.state = {
            displayedContent: ContentType.Repository,
        };
    }

    render() {
        if (this.state.displayedContent === ContentType.Repository) {
            return (
                <RepoDetail
                    displayedType={this.state.displayedContent}
                    setDisplayedType={x => this.setDisplayedType(x)}
                    namespace={this.props.namespace}
                    injector={this.props.injector}
                />
            );
        } else {
            return (
                <CollectionDetail
                    displayedType={this.state.displayedContent}
                    setDisplayedType={x => this.setDisplayedType(x)}
                />
            );
        }
    }

    private setDisplayedType(type: ContentType) {
        this.setState({ displayedContent: type });
    }
}
