import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';
import { NotFoundComponent }     from './exception-pages/not-found/not-found.component';
import { AuthorDetailComponent } from './authors/detail/author-detail.component'
import {
    NamespaceDetailResolver,
    RepositoryResolver as AuthorRepositoryResolver
}  from './authors/authors.resolver.service';

import { ContentDetailComponent } from './content-detail/content-detail.component';
import {
    ContentResolver,
    RepositoryResolver as ContentRepositoryResolver,
    NamespaceResolver
} from './content-detail/content-detail.resolver.service';


const appRoutes: Routes = [
    {
        path: '',
        redirectTo: '/home',
        pathMatch: 'full'
    }, {
        path: 'my-imports',
        loadChildren: './my-imports/my-imports.module#MyImportsModule'
    }, {
        path: 'my-content',
        loadChildren: './my-content/my-content.module#MyContentModule'
    }, {
        path: ':namespace/:repository/:content_name',
        component: ContentDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: ContentRepositoryResolver,
            namespace: NamespaceResolver
        }
    }, {
        path: ':namespace/:repository',
        component: ContentDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: ContentRepositoryResolver,
            namespace: NamespaceResolver
        }
    }, {
        path: ':namespace',
        component: AuthorDetailComponent,
        resolve: {
            namespace: NamespaceDetailResolver,
            repositories: AuthorRepositoryResolver
        }
    }, {
        path: '**',
        component: NotFoundComponent
    }
];

@NgModule({
    imports: [
        RouterModule.forRoot(appRoutes, {
            enableTracing: false,
            onSameUrlNavigation: 'reload'
        })
    ],
    exports: [ RouterModule ]
})
export class AppRoutingModule { }
