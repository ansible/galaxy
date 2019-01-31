import { Component, OnInit } from '@angular/core';

import { CommunityPage } from './react-components/community-page';
import { Render } from './react-components/render-react';

import { Injector } from '@angular/core';

@Component({
    selector: 'app-authors',
    template: '<div id="react-container"></div>',
    styles: [''],
})
export class AuthorsReactComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'AuthorsReactComponent';

    constructor(public injector: Injector) {}

    ngOnInit() {
        Render.init(this.injector, CommunityPage, 'react-container');
    }
}
