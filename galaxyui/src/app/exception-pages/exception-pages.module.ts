import { NgModule }     from '@angular/core';
import { CommonModule } from '@angular/common';

import { ActionModule }     from 'patternfly-ng/action/action.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';

import { PageHeaderModule }            from '../page-header/page-header.module';
import { AccessDeniedComponent }       from './access-denied/access-denied.component';
import { NotFoundComponent }           from './not-found/not-found.component';
import { ExceptionPagesRoutingModule } from './exception-pages.routing.module';

@NgModule({
    declarations: [
        AccessDeniedComponent,
        NotFoundComponent
    ],
    imports: [
        ActionModule,
        CommonModule,
        PageHeaderModule,
        ExceptionPagesRoutingModule,
        EmptyStateModule,
    ],
})
export class ExceptionPagesModule {}
