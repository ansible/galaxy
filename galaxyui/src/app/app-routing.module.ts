import { NgModule } from '@angular/core';
import { AuthorDetailComponent } from './authors/detail/author-detail.component';
import { RepositoryDetailComponent } from './content-detail/repository-detail/repository-detail.component';
import { CollectionDetailComponent } from './content-detail/collection-detail/collection-detail.component';
import { NotFoundComponent } from './exception-pages/not-found/not-found.component';

import {
    ContentResolver,
    NamespaceResolver,
    RepositoryResolver as ContentRepositoryResolver,
    CollectionResolver,
} from './content-detail/content-detail.resolver.service';

import {
    NamespaceDetailResolver,
    RepositoryCollectionResolver,
} from './authors/authors.resolver.service';

import { PreloadAllModules, RouterModule, Routes } from '@angular/router';

const appRoutes: Routes = [
    // Lazily loaded modules
    {
        path: 'search',
        loadChildren: './search/search.module#SearchModule',
    },
    {
        path: 'my-content',
        loadChildren: './my-content/my-content.module#MyContentModule',
    },
    {
        path: 'my-imports',
        loadChildren: './my-imports/my-imports.module#MyImportsModule',
    },

    // Routes that resolve variables have to go in app-routing.module to ensure
    // that they are resolved between the static routes ('/search', '/my-content' etc)
    // and the wildcard ('**')

    // Repository Routes
    {
        path: 'repositories/:namespace/:repository/:content_name',
        component: RepositoryDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: ContentRepositoryResolver,
            namespace: NamespaceResolver,
        },
    },
    {
        path: 'repositories/:namespace/:repository',
        component: RepositoryDetailComponent,
        resolve: {
            content: ContentResolver,
            repository: ContentRepositoryResolver,
            namespace: NamespaceResolver,
        },
    },
    {
        path: 'repositories/:namespace',
        redirectTo: ':namespace',
    },
    {
        path: 'repositories',
        redirectTo: 'search',
    },

    // Collection Routes
    {
        path: 'collections/:namespace/:collection',
        component: CollectionDetailComponent,
        resolve: {
            collection: CollectionResolver,
        },
    },
    {
        path: 'collections/:namespace',
        redirectTo: ':namespace',
    },
    {
        path: 'collections',
        redirectTo: 'search',
    },

    // Legacy repository routes
    {
        path: ':namespace/:repository/:content_name',
        redirectTo: 'repositories/:namespace/:repository/:content_name',
    },
    {
        path: ':namespace/:repository',
        redirectTo: 'repositories/:namespace/:repository',
    },
    {
        path: ':namespace',
        component: AuthorDetailComponent,
        resolve: {
            namespace: NamespaceDetailResolver,
            content: RepositoryCollectionResolver,
        },
    },
    {
        path: '**',
        component: NotFoundComponent,
    },
];

@NgModule({
    imports: [
        RouterModule.forRoot(appRoutes, {
            enableTracing: false,
            onSameUrlNavigation: 'reload',
            preloadingStrategy: PreloadAllModules,
        }),
    ],
    exports: [RouterModule],
})
export class AppRoutingModule {}
