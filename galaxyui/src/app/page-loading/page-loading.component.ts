import {
    Component,
    OnInit,
    Input
} from '@angular/core';

@Component({
    selector: 'app-page-loading',
    templateUrl: './page-loading.component.html',
    styleUrls: ['./page-loading.component.less']
})
export class PageLoadingComponent implements OnInit {
    @Input() loading: boolean;

    constructor() { }

    ngOnInit() {}
}
