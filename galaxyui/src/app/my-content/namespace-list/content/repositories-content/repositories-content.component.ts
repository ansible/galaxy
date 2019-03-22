import {
    Component,
    OnDestroy,
    OnInit,
    ViewEncapsulation,
    Injector,
    ViewChild,
    ElementRef,
    Input,
} from '@angular/core';

import { Namespace } from '../../../../resources/namespaces/namespace';
import { Render } from '../../../../react/lib/render-react';
import { ContentDetailContainer } from '../../../../react/containers/my-content/content-detail';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'repositories-content',
    template: '<div #reactContainer></div>',
    styles: [''],
})
export class RepositoriesContentComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'RepositoriesContentComponent';

    @ViewChild('reactContainer')
    reactContainer: ElementRef;

    @Input()
    contentAdded: any;

    @Input()
    namespace: Namespace;

    constructor(public injector: Injector) {}

    ngOnInit() {
        Render.init(
            this.injector,
            ContentDetailContainer,
            this.reactContainer.nativeElement,
            {
                namespace: this.namespace,
            },
        );
    }

    ngOnDestroy() {
        Render.unmount(this.reactContainer.nativeElement);
    }
}
