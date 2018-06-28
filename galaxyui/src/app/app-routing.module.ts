import { NgModule }              from '@angular/core';
import { NotFoundComponent }     from './exception-pages/not-found/not-found.component';
import { AuthorDetailComponent } from './authors/detail/author-detail.component';
import { ContentDetailComponent } from './content-detail/content-detail.component';

import {
    ContentResolver,
    RepositoryResolver as ContentRepositoryResolver,
    NamespaceResolver
} from './content-detail/content-detail.resolver.service';

import {
    NamespaceDetailResolver,
    RepositoryResolver as AuthorRepositoryResolver
}  from './authors/authors.resolver.service';


import {
    RouterModule,
    Routes,
    PreloadAllModules
}  from '@angular/router';


const appRoutes: Routes = [
    {
        path: '',
        redirectTo: '/home',
        pathMatch: 'full'
    }, {
        path: 'search',
        loadChildren: './search/search.module#SearchModule'
    }, {
        path: 'my-content',
        loadChildren: './my-content/my-content.module#MyContentModule'
    }, {
        path: 'my-imports',
        loadChildren: './my-imports/my-imports.module#MyImportsModule'
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
            onSameUrlNavigation: 'reload',
            preloadingStrategy: PreloadAllModules
        })
    ],
    exports: [ RouterModule ]
})
export class AppRoutingModule { }
