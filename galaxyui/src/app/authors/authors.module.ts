import { CommonModule }    from '@angular/common';
import { NgModule }        from '@angular/core';

import { TooltipModule }           from 'ngx-bootstrap/tooltip';
import { ActionModule }            from 'patternfly-ng/action/action.module';
import { EmptyStateModule }        from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }            from 'patternfly-ng/filter/filter.module';
import { ListModule }              from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule }        from 'patternfly-ng/pagination/pagination.module';
import { ToolbarModule }           from 'patternfly-ng/toolbar/toolbar.module';

import { AuthorsComponent }          from './authors.component';
import { AuthorsRoutingModule }      from './authors.routing.module';
import { AuthorDetailComponent }     from './detail/author-detail.component';
import { DetailActionsComponent }    from './detail/detail-actions/detail-actions.component';

import { SharedModule }                from '../shared/shared.module';

@NgModule({
    imports: [
        CommonModule,
        EmptyStateModule,
        ListModule,
        PaginationModule,
        FilterModule,
        ToolbarModule,
        TooltipModule,
        AuthorsRoutingModule,
        ActionModule,
        SharedModule
    ],
    declarations: [
        DetailActionsComponent,
        AuthorsComponent,
        AuthorDetailComponent
    ]
})
export class AuthorsModule { }
