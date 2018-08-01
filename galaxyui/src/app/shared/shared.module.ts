import { NgModule }          from '@angular/core';

import { RouterModule }        from '@angular/router';

import { CommonModule }      from '@angular/common';

import { LogEventDirective } from './directives/log-event.directive';

import { ClipboardComponent }   from './components/clipboard/clipboard.component';
import { PageHeaderComponent }  from './components/page-header/page-header.component';
import { PageLoadingComponent } from './components/page-loading/page-loading.component';

@NgModule({
    imports: [
        CommonModule,
        RouterModule
    ],
    declarations: [
        LogEventDirective,
        ClipboardComponent,
        PageHeaderComponent,
        PageLoadingComponent
    ],
    exports: [
        LogEventDirective,
        ClipboardComponent,
        PageHeaderComponent,
        PageLoadingComponent
    ],
})
export class SharedModule {
    constructor() {}
}
