import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { PageHeader } from './page-header';
import { Injector } from '@angular/core';
import { InjectorContext } from './injector-context';

interface ICommunityProp {
    headerIcon: string;
    headerTitle: string;
}

class CommunityComponent extends React.Component<ICommunityProp, {}> {
    render() {
        return (
            <PageHeader
                headerIcon={this.props.headerIcon}
                headerTitle='Community Authors;/community;geerlingguy;/geerlingguy;php'
            />
        );
    }
}

export default class CommunityRenderer {
    static init(headerIcon: string, headerTitle: string, injector: Injector) {
        ReactDOM.render(
            <InjectorContext.Provider value={{ injector: injector }}>
                <CommunityComponent
                    headerIcon={headerIcon}
                    headerTitle={headerTitle}
                />
            </InjectorContext.Provider>,
            document.getElementById('react-container'),
        );
    }
}
