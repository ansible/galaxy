import { Component, OnInit } from '@angular/core';

import CommunityPageRenderer from './react-components/community-page';

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
        CommunityPageRenderer.init(this.injector);
    }
}
