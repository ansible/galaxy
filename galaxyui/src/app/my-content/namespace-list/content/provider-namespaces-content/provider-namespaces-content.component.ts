import { Component, Input, OnInit, ViewEncapsulation } from '@angular/core';

import { Namespace } from '../../../../resources/namespaces/namespace';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'provider-namespaces-content',
    templateUrl: './provider-namespaces-content.component.html',
    styleUrls: ['./provider-namespaces-content.component.less'],
})
export class ProviderNamespacesContentComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ProviderNamespacesContentComponent';

    @Input()
    namespace: Namespace;

    constructor() {}

    ngOnInit() {}
}
