import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExploreComponent } from './explore.component';

import { ExploreRoutingModule } from './explore.routing.module'
import { PageHeaderModule }     from '../page-header/page-header.module';

import {
	CardModule
} from 'patternfly-ng/card/card.module';

@NgModule({
  imports: [
    CommonModule,
    ExploreRoutingModule,
    PageHeaderModule,
    CardModule
  ],
  declarations: [ExploreComponent]
})
export class ExploreModule { }
