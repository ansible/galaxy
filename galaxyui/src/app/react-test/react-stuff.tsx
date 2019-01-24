import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { Link } from '../authors-react/react-components/link';
import { Injector } from '@angular/core';
import { InjectorContext } from '../authors-react/react-components/injector-context';

class Test extends React.Component<{}, {}> {
    render() {
        return (
            <div>
                <h1>Hello World</h1>
                <Link to='/home'>Go home Buddy, I work alone</Link>
            </div>
        );
    }
}

export class TestComponent {
    static init(injector: Injector) {
        ReactDOM.render(
            <InjectorContext.Provider value={{ injector: injector }}>
                <Test />
            </InjectorContext.Provider>,

            document.getElementById('react-container'),
        );
    }
}
