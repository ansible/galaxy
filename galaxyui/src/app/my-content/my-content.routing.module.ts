import { NgModule }                 from '@angular/core';

import {
    RouterModule,
    Routes
} from '@angular/router';

import { AuthService }              from '../auth/auth.service';
import { NamespaceDetailComponent } from './namespace-detail/namespace-detail.component';

import {
    NamespaceDetailResolver,
    MeResolver
}  from './namespace-detail/namespace-detail.resolver.service';

import { NamespaceListComponent }   from './namespace-list/namespace-list.component';
import { NamespaceListResolver }    from './namespace-list/namespace-list-resolver.service';

const myContentRoutes: Routes = [
    {
        path: 'my-content',
        redirectTo: 'my-content/namespaces',
        pathMatch: 'full',
        canActivate: [AuthService]
    },
    {
        path: 'my-content/namespaces/:id',
        component: NamespaceDetailComponent,
        resolve: {
            me: MeResolver,
            namespace: NamespaceDetailResolver
        },
        canActivate: [AuthService]
    },
    {
        path: 'my-content/namespaces',
        component: NamespaceListComponent,
        resolve: {
            me: MeResolver,
            namespaces: NamespaceListResolver
        },
        canActivate: [AuthService]
    }
];

@NgModule({
    imports: [
        RouterModule.forChild(myContentRoutes)
    ],
    exports: [
        RouterModule,
    ],
    providers: [
        NamespaceDetailResolver,
        NamespaceListResolver,
        MeResolver
    ]
})
export class MyContentRoutingModule {
}
