import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { NamespaceDetailComponent } from './namespace-detail/namespace-detail.component';
import { NamespaceDetailResolver }  from './namespace-detail/namespace-detail-resolver.service';
import { NamespaceListComponent }   from './namespace-list/namespace-list.component';
import { NamespaceListResolver }    from './namespace-list/namespace-list-resolver.service';

const myContentRoutes: Routes = [
    {
        path: 'my-content',
        redirectTo: 'my-content/namespaces',
        pathMatch: 'full'
    },
    {
        path: 'my-content/namespaces/:id',
        component: NamespaceDetailComponent,
        resolve: {
            namespace: NamespaceDetailResolver
        }
    },
    {
        path: 'my-content/namespaces',
        component: NamespaceListComponent,
        resolve: {
            namespaces: NamespaceListResolver
        }
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
        NamespaceListResolver
    ]
})
export class MyContentRoutingModule {
}
