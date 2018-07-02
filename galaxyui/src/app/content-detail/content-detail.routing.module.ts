import { NgModule } from '@angular/core';

import {
    Routes,
    RouterModule
} from '@angular/router';

import { ContentDetailComponent } from './content-detail.component';
import {
    ContentResolver,
    RepositoryResolver,
    NamespaceResolver
} from './content-detail.resolver.service';

const routes: Routes = [
    // ':namespace/:repository/:content_name' and ':namespace/:repository/ moved
    // to app-routing.module
];

@NgModule({
    imports: [
          RouterModule.forChild(routes)
      ],
      exports: [
          RouterModule
      ],
      providers: [
          ContentResolver,
          RepositoryResolver,
          NamespaceResolver
      ]
})
export class ContentDetailRoutingModule { }
