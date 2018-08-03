import { Component, Input, OnInit, ViewEncapsulation } from '@angular/core';
import { Namespace } from '../../../../resources/namespaces/namespace';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'owners-content',
    templateUrl: './owners-content.component.html',
    styleUrls: ['./owners-content.component.less'],
})
export class OwnersContentComponent implements OnInit {
    @Input()
    namespace: Namespace;

    constructor() {}

    ngOnInit() {}
}
