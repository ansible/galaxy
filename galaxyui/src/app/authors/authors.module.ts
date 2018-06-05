import { NgModule }        from '@angular/core';
import { CommonModule }    from '@angular/common';

import { ActionModule }            from 'patternfly-ng/action/action.module';
import { EmptyStateModule }        from 'patternfly-ng/empty-state/empty-state.module'
import { ListModule }              from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule }        from 'patternfly-ng/pagination/pagination.module';
import { FilterModule }            from 'patternfly-ng/filter/filter.module';
import { ToolbarModule }           from 'patternfly-ng/toolbar/toolbar.module';
import { TooltipModule }           from 'ngx-bootstrap/tooltip';

import { AuthorsRoutingModule }      from './authors.routing.module';
import { AuthorsComponent }          from './authors.component';
import { AuthorDetailComponent }     from './detail/author-detail.component';
import { DetailActionsComponent }    from './detail/detail-actions/detail-actions.component';
import { PageHeaderModule }          from '../page-header/page-header.module';
import { PageLoadingModule }         from '../page-loading/page-loading.module';


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
        PageHeaderModule,
        PageLoadingModule,
        ActionModule
    ],
    declarations: [
        DetailActionsComponent,
        AuthorsComponent,
        AuthorDetailComponent
    ]
})
export class AuthorsModule { }
