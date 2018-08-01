import { NgModule }           from '@angular/core';

import { CommonModule }       from '@angular/common';

import { LogEventDirective }  from './directives/log-event.directive';

@NgModule({
    imports: [
        CommonModule,
    ],
    declarations: [
        LogEventDirective,
    ],
    exports: [
        LogEventDirective,
    ],
})
export class SharedModule {
    constructor() {}
}
