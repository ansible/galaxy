import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';
import { NotFoundComponent }     from './exception-pages/not-found/not-found.component';
import { AuthorDetailComponent } from './authors/detail/author-detail.component'
import {
    NamespaceDetailResolver,
    RepositoryResolver
}  from './authors/authors.resolver.service';



const appRoutes: Routes = [
    {
        path: '',
        redirectTo: '/home',
        pathMatch: 'full'
    }, {
        path: ':namespace',
        component: AuthorDetailComponent,
        resolve: {
            namespace: NamespaceDetailResolver,
            repositories: RepositoryResolver
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
