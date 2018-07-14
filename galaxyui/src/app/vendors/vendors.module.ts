import { CommonModule }    from '@angular/common';
import { NgModule }        from '@angular/core';

import { TooltipModule }           from 'ngx-bootstrap/tooltip';
import { ActionModule }            from 'patternfly-ng/action/action.module';
import { EmptyStateModule }        from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }            from 'patternfly-ng/filter/filter.module';
import { ListModule }              from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule }        from 'patternfly-ng/pagination/pagination.module';
import { ToolbarModule }           from 'patternfly-ng/toolbar/toolbar.module';

import { PageHeaderModule }        from '../page-header/page-header.module';
import { PageLoadingModule }       from '../page-loading/page-loading.module';
import { VendorCardComponent }     from './card/vendor-card.component';
import { VendorsComponent }        from './vendors.component';
import { VendorsRoutingModule }    from './vendors.routing.module';

@NgModule({
    imports: [
        CommonModule,
        EmptyStateModule,
        ListModule,
        PaginationModule,
        FilterModule,
        ToolbarModule,
        TooltipModule,
        VendorsRoutingModule,
        PageHeaderModule,
        PageLoadingModule,
        ActionModule
    ],
    declarations: [
        VendorsComponent,
        VendorCardComponent
    ]
})
export class VendorsModule { }
