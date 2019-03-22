import {
    Component,
    OnInit,
    OnDestroy,
    ViewChild,
    ElementRef,
    Injector,
} from '@angular/core';

import { AddContentModalContainer } from '../../react/containers/add-content-container';
import { Render } from '../../react/lib/render-react';

import { Namespace } from '../../resources/namespaces/namespace';

@Component({
    selector: 'add-repository-modal',
    template: '<div #reactContainer></div>',
    styles: [''],
})
export class AddContentModalComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'AddContentModalComponent';

    @ViewChild('reactContainer')
    reactContainer: ElementRef;
    namespace: Namespace;
    collectionName: string;

    // The Namespace list component expects this property to be set on the modal
    // so that it knows when to start polling the API for import updates.
    // Angular can't read properties off of the React components so this value
    // unfortunately needs to be passed back up to the angular component.
    repositoriesAdded = false;

    constructor(public injector: Injector) {}

    ngOnInit() {
        Render.init(
            this.injector,
            AddContentModalContainer,
            this.reactContainer.nativeElement,
            {
                namespace: this.namespace,
                updateAdded: x => this.updateRepositoriesAdded(x),
                collectionName: this.collectionName,
            },
        );
    }

    ngOnDestroy() {
        Render.unmount(this.reactContainer.nativeElement);
    }

    private updateRepositoriesAdded(added) {
        this.repositoriesAdded = added;
    }
}
