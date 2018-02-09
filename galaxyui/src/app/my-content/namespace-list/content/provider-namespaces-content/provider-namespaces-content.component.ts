import { Component, OnInit, Input, ViewEncapsulation } from '@angular/core';

import { Namespace }                                   from "../../../../resources/namespaces/namespace";

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'provider-namespaces-content',
    templateUrl: './provider-namespaces-content.component.html',
    styleUrls: ['./provider-namespaces-content.component.less']
})
export class ProviderNamespacesContentComponent implements OnInit {
    @Input() namespace: Namespace;

    constructor() {
    }

    ngOnInit() {
    }

}
