import { Component, OnInit } from '@angular/core';
import { TestComponent } from './react-stuff';

@Component({
    selector: 'app-react-test',
    templateUrl: './react-test.component.html',
    styleUrls: ['./react-test.component.less'],
})
export class ReactTestComponent implements OnInit {
    constructor() {}

    ngOnInit() {
        TestComponent.init();
    }
}
