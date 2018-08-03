import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { BsDropdownModule } from 'ngx-bootstrap';

import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { ActionModule } from 'patternfly-ng/action/action.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule } from 'patternfly-ng/filter/filter.module';
import { ListModule } from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule } from 'patternfly-ng/pagination/pagination.module';
import { SortModule } from 'patternfly-ng/sort/sort.module';
import { ToolbarModule } from 'patternfly-ng/toolbar/toolbar.module';

import { PopularComponent } from './popular/popular.component';
import { SearchRoutingModule } from './search-routing.module';
import { SearchComponent } from './search.component';

import { PageHeaderModule } from '../page-header/page-header.module';
import { PageLoadingModule } from '../page-loading/page-loading.module';

@NgModule({
    imports: [
        ActionModule,
        EmptyStateModule,
        FilterModule,
        SortModule,
        ToolbarModule,
        TooltipModule,
        ListModule,
        CommonModule,
        SearchRoutingModule,
        PageHeaderModule,
        PageLoadingModule,
        PaginationModule,
        BsDropdownModule.forRoot(),
    ],
    declarations: [SearchComponent, PopularComponent],
})
export class SearchModule {}
