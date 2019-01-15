import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import {
    NamespaceDetailResolver,
    NamespaceListResolver,
    RepositoryResolver,
} from './authors-react.resolver.service';

import { AuthorsReactComponent } from './authors-react.component';

const routes: Routes = [
    {
        path: 'community-react',
        component: AuthorsReactComponent,
        resolve: {
            namespaces: NamespaceListResolver,
        },
    },
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
export class AuthorsReactRoutingModule {}
