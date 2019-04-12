import {
    Component,
    OnDestroy,
    OnInit,
    Injector,
    ViewChild,
    ElementRef,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Render } from '../../react/lib/render-react';

import {
    CollectionImport,
    RepoImport,
    ImportList,
} from '../../resources/imports/import';

import { MyImportsPage } from '../../react/containers/my-imports';

@Component({
    selector: 'import-list',
    template: '<div #reactContainer></div>',
    styles: [''],
})
export class ImportListComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'ImportListComponent';

    @ViewChild('reactContainer')
    reactContainer: ElementRef;

    constructor(public injector: Injector, private route: ActivatedRoute) {}

    ngOnInit() {
        this.route.params.subscribe(params => {
            this.route.data.subscribe(data => {
                const props = { namespaces: data.namespaces.results };

                if (data.importList) {
                    props['importList'] = data.importList;
                    props['selectedNamespace'] = parseInt(
                        params['namespaceid'],
                        10,
                    );
                }

                Render.init(
                    this.injector,
                    MyImportsPage,
                    this.reactContainer.nativeElement,
                    props,
                );
            });
        });
    }

    ngOnDestroy() {
        Render.unmount(this.reactContainer.nativeElement);
    }
}
