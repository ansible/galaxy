import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExploreComponent } from './explore.component';

import { ExploreRoutingModule } from './explore.routing.module'

@NgModule({
  imports: [
    CommonModule,
    ExploreRoutingModule,
  ],
  declarations: [ExploreComponent]
})
export class ExploreModule { }
