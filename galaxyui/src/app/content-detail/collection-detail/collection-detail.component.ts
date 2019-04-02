import { Component, OnInit } from '@angular/core';

@Component({
    selector: 'app-collection-detail',
    templateUrl: './collection-detail.component.html',
    styleUrls: ['./collection-detail.component.less'],
})
export class CollectionDetailComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CollectionDetailComponent';

    constructor() {}

    ngOnInit() {}
}
