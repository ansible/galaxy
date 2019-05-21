import { NgModule } from '@angular/core';
import { AuthorDetailComponent } from './authors/detail/author-detail.component';
import { DetailLoaderComponent } from './content-detail/detail-loader.component';
import { NotFoundComponent } from './exception-pages/not-found/not-found.component';

import {
    NamespaceDetailResolver,
    RepositoryCollectionResolver,
} from './authors/authors.resolver.service';

import { TypeCheckResolver } from './content-detail/content-detail.resolver.service';

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

    // Legacy repository routes
    {
        path: ':namespace/:name/:content_name',
        component: DetailLoaderComponent,
        resolve: {
            contentType: TypeCheckResolver,
        },
    },
    {
        path: ':namespace/:name',
        component: DetailLoaderComponent,
        resolve: {
            contentType: TypeCheckResolver,
        },
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
