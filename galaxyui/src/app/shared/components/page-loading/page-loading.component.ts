import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-page-loading',
    templateUrl: './page-loading.component.html',
    styleUrls: ['./page-loading.component.less'],
})
export class PageLoadingComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'PageLoadingComponent';

    @Input()
    loading: boolean;

    constructor() {}

    ngOnInit() {}
}
