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
    {
        path: ':namespace/:repository/:content_name',
        component: ContentDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: RepositoryResolver,
            namespace: NamespaceResolver
        }
    },
    {
        path: ':namespace/:repository',
        component: ContentDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: RepositoryResolver,
            namespace: NamespaceResolver
        }
    },
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
