import { NgModule }                  from '@angular/core';
import { CommonModule }              from '@angular/common';

import { ActionModule }              from 'patternfly-ng/action/action.module';
import { EmptyStateModule }          from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }              from 'patternfly-ng/filter/filter.module';
import { ToolbarModule }             from 'patternfly-ng/toolbar/toolbar.module';
import { ListModule }                from 'patternfly-ng/list/list.module';

import { ImportListComponent }       from './import-list/import-list.component';
import { ImportDetailComponent }     from './import-detail/import-detail.component';
import { MyImportsRoutingModule }    from './my-imports.routing.module';

import { PageHeaderModule }          from '../page-header/page-header.module';
import { PageLoadingModule }         from '../page-loading/page-loading.module';

@NgModule({
    imports: [
        ActionModule,
        EmptyStateModule,
        FilterModule,
        ToolbarModule,
        ListModule,
        CommonModule,
        PageHeaderModule,
        PageLoadingModule,
        MyImportsRoutingModule
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
