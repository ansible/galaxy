import {
    Component,
    OnInit,
    OnDestroy,
    ViewChild,
    ElementRef,
} from '@angular/core';

import { AddRepositoryModalContainer } from '../../react/containers/add-repository-container';
import { Render } from '../../react/lib/render-react';

import { Injector } from '@angular/core';

import { Namespace } from '../../resources/namespaces/namespace';

@Component({
    selector: 'add-repository-modal',
    template: '<div #reactContainer></div>',
    styles: [''],
})
export class AddRepositoryModalComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'AddRepositoryModalComponent';

    @ViewChild('reactContainer')
    reactContainer: ElementRef;
    namespace: Namespace;

    // The Namespace list component expects this property to be set on the modal
    // so that it knows when to start polling the API for import updates.
    // Angular can't reat properties off of the React components so this value
    // unfortunately needs to be passed back up to the angular component.
    repositoriesAdded = false;

    constructor(public injector: Injector) {}

    ngOnInit() {
        Render.init(
            this.injector,
            AddRepositoryModalContainer,
            this.reactContainer.nativeElement,
            {
                namespace: this.namespace,
                updateAdded: x => this.updateRepositoriesAdded(x),
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
