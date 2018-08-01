import { CommonModule }              from '@angular/common';
import { NgModule }                  from '@angular/core';

import { ActionModule }              from 'patternfly-ng/action/action.module';
import { EmptyStateModule }          from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }              from 'patternfly-ng/filter/filter.module';
import { ListModule }                from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule }          from 'patternfly-ng/pagination/pagination.module';
import { ToolbarModule }             from 'patternfly-ng/toolbar/toolbar.module';

import { TooltipModule }             from 'ngx-bootstrap/tooltip';

import { ImportDetailComponent }     from './import-detail/import-detail.component';
import { ImportListComponent }       from './import-list/import-list.component';
import { MyImportsRoutingModule }    from './my-imports.routing.module';

import { SharedModule }                from '../shared/shared.module';

@NgModule({
    imports: [
        TooltipModule.forRoot(),
        ActionModule,
        EmptyStateModule,
        FilterModule,
        ToolbarModule,
        ListModule,
        CommonModule,
        PaginationModule,
        MyImportsRoutingModule,
        SharedModule
    ],
    declarations: [
        ImportListComponent,
        ImportDetailComponent
    ],
    exports: [
        ImportDetailComponent
    ]
})
export class MyImportsModule {}
