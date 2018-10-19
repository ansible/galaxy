import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import {
    NamespaceDetailResolver,
    NamespaceListResolver,
    RepositoryResolver,
} from './authors.resolver.service';

import { AuthorsComponent } from './authors.component';

const routes: Routes = [
    {
        path: 'community',
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
        RepositoryResolver,
    ],
})
export class AuthorsRoutingModule {}
