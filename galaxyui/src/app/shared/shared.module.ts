import { NgModule } from '@angular/core';

import { RouterModule } from '@angular/router';

import { CommonModule } from '@angular/common';

import { LogButtonLinkDirective } from './directives/log-event.directive';

import { PageHeaderComponent } from './components/page-header/page-header.component';
import { PageLoadingComponent } from './components/page-loading/page-loading.component';

@NgModule({
    imports: [CommonModule, RouterModule],
    declarations: [LogButtonLinkDirective, PageHeaderComponent, PageLoadingComponent],
    exports: [LogButtonLinkDirective, PageHeaderComponent, PageLoadingComponent],
})
export class SharedModule {
    constructor() {}
}
