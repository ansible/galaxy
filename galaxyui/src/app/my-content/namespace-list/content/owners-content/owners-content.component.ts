import { Component, OnInit, Input, ViewEncapsulation } from '@angular/core';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'owners-content',
    templateUrl: './owners-content.component.html',
    styleUrls: ['./owners-content.component.less']
})
export class OwnersContentComponent implements OnInit {
    @Input() item: any;

    constructor() {
    }

    ngOnInit() {
    }

}
