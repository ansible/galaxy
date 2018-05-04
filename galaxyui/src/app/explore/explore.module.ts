import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExploreComponent } from './explore.component';

import { ExploreRoutingModule } from './explore.routing.module'
import { PageHeaderModule }     from '../page-header/page-header.module';
import { ListModule } from 'patternfly-ng/list/list.module';

import {
	CardModule
} from 'patternfly-ng/card/card.module';
import { TopListComponent } from './top-list/top-list.component';

@NgModule({
  imports: [
    CommonModule,
    ExploreRoutingModule,
    PageHeaderModule,
    CardModule,
		ListModule
  ],
  declarations: [ExploreComponent, TopListComponent]
})
export class ExploreModule { }
