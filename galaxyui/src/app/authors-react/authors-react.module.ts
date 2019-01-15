import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { ActionModule } from 'patternfly-ng/action/action.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule } from 'patternfly-ng/filter/filter.module';
import { ListModule } from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule } from 'patternfly-ng/pagination/pagination.module';
import { ToolbarModule } from 'patternfly-ng/toolbar/toolbar.module';
import { UtilitiesModule } from '../utilities/utilities.module';

import { SharedModule } from '../shared/shared.module';
import { AuthorsReactComponent } from './authors-react.component';
import { AuthorsReactRoutingModule } from './authors-react.routing.module';

@NgModule({
    imports: [
        CommonModule,
        EmptyStateModule,
        ListModule,
        PaginationModule,
        FilterModule,
        ToolbarModule,
        TooltipModule,
        AuthorsReactRoutingModule,
        SharedModule,

        ActionModule,
        UtilitiesModule,
    ],
    declarations: [AuthorsReactComponent],
})
export class AuthorsReactModule {}
