import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import {
    NamespaceDetailResolver,
    NamespaceListResolver,
    RepositoryCollectionResolver,
} from './authors.resolver.service';

import { AuthorsComponent } from './authors.component';

const routes: Routes = [
    {
        path: 'authors',
        component: AuthorsComponent,
        resolve: {
            namespaces: NamespaceListResolver,
        },
    },
    // ':namespace/ moved to app-routing.module
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: [
        NamespaceDetailResolver,
        NamespaceListResolver,
        RepositoryCollectionResolver,
    ],
})
export class AuthorsRoutingModule {}
