import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { ActionModule } from 'patternfly-ng/action/action.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';

import { PageHeaderModule } from '../page-header/page-header.module';
import { AccessDeniedComponent } from './access-denied/access-denied.component';
import { ExceptionPagesRoutingModule } from './exception-pages.routing.module';
import { NotFoundComponent } from './not-found/not-found.component';

@NgModule({
    declarations: [AccessDeniedComponent, NotFoundComponent],
    imports: [ActionModule, CommonModule, PageHeaderModule, ExceptionPagesRoutingModule, EmptyStateModule],
})
export class ExceptionPagesModule {}
