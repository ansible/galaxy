import * as React from 'react';
import { Router } from '@angular/router';
import { InjectorContext } from './injector-context';

interface ILinkProp {
    to: string;
    replace?: boolean;
    innerRef?: () => void;
    onClick?: (event, injector) => void;
    target?: string;
    className?: string;
}

function isModifiedEvent(event) {
    return !!(event.metaKey || event.altKey || event.ctrlKey || event.shiftKey);
}

export class Link extends React.Component<ILinkProp, {}> {
    // This class is intended to mock the Link component from React Router.
    // https://github.com/ReactTraining/react-router/blob/cc18b36a8bb3f42c312fa2b9f625429f9b8ae921/packages/react-router-dom/modules/Link.js#L14
    // Eventually we want to migrate everything from the Angular router to
    // React router. This class is intended to make the migration process easier
    // by providing the same interface that React Router uses for the Angular
    // router. By using this compment we should be able to migrate over to React
    // Router by simply swapping any imports of this class for the one provided
    // by React Router.

    static contextType = InjectorContext;

    handleClick(event, injector) {
        if (this.props.onClick) this.props.onClick(event, injector);

        if (
            // onClick prevented default
            !event.defaultPrevented &&
            // ignore everything but left clicks
            event.button === 0 &&
            // let browser handle "target=_blank" etc.
            (!this.props.target || this.props.target === '_self') &&
            // ignore clicks with modifier keys
            !isModifiedEvent(event)
        ) {
            event.preventDefault();

            let router = injector.get(Router);

            router.navigateByUrl(this.props.to);
        }
    }

    render() {
        const { to, replace, innerRef, ...rest } = this.props; // eslint-disable-line no-unused-vars

        // InjectorContext allows us to inject instantiated services from
        // Angular into React. We use this to get a reference to the Angular
        // router service for navigation purposes.
        // For this to work, one of the parents of this class needs to be able
        // to provide an instance of the Angular injector service as a React
        // context object to this component
        return (
            <InjectorContext.Consumer>
                {context => {
                    return (
                        <a
                            {...rest}
                            onClick={event =>
                                this.handleClick(event, context.injector)
                            }
                            href={to}
                            ref={innerRef}
                        />
                    );
                }}
            </InjectorContext.Consumer>
        );
    }
}
