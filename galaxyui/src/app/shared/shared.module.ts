import { NgModule } from '@angular/core';

import { RouterModule } from '@angular/router';

import { CommonModule } from '@angular/common';

import { LogButtonLinkDirective } from './directives/log-event.directive';
import { MiddleclickDirective } from './directives/middleclick.directive';

import { PageHeaderComponent } from './components/page-header/page-header.component';
import { PageLoadingComponent } from './components/page-loading/page-loading.component';

@NgModule({
    imports: [CommonModule, RouterModule],
    declarations: [LogButtonLinkDirective, PageHeaderComponent, PageLoadingComponent, MiddleclickDirective],
    exports: [LogButtonLinkDirective, PageHeaderComponent, PageLoadingComponent, MiddleclickDirective],
})
export class SharedModule {
    constructor() {}
}
