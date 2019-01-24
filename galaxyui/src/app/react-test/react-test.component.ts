import { Component, OnInit } from '@angular/core';
import { TestComponent } from './react-stuff';
import { Injector } from '@angular/core';

@Component({
    selector: 'app-react-test',
    templateUrl: './react-test.component.html',
    styleUrls: ['./react-test.component.less'],
})
export class ReactTestComponent implements OnInit {
    constructor(private injector: Injector) {}

    ngOnInit() {
        TestComponent.init(this.injector);
    }
}
