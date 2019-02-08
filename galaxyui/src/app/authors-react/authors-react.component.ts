import {
    Component,
    OnInit,
    OnDestroy,
    ViewChild,
    ElementRef,
} from '@angular/core';

import { CommunityPage } from '../react/containers/community-page';
import { Render } from '../react/lib/render-react';

import { Injector } from '@angular/core';

@Component({
    selector: 'app-authors',
    template: '<div #reactContainer></div>',
    styles: [''],
})
export class AuthorsReactComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'AuthorsReactComponent';
    @ViewChild('reactContainer')
    reactContainer: ElementRef;

    constructor(public injector: Injector) {}

    ngOnInit() {
        Render.init(
            this.injector,
            CommunityPage,
            this.reactContainer.nativeElement,
        );
    }

    ngOnDestroy() {
        Render.unmount(this.reactContainer.nativeElement);
    }
}
