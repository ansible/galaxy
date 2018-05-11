import {
       NgModule

} from '@angular/core';

import {
	Routes,
	RouterModule
} from '@angular/router';

import {
    NamespaceDetailResolver,
    NamespaceListResolver,
    RepositoryResolver
}  from './authors.resolver.service';

import { AuthorsComponent }         from './authors.component';
import { AuthorDetailComponent }    from './detail/author-detail.component';


const routes: Routes = [{
    	path: 'authors',
    	component: AuthorsComponent,
    	resolve: {
    		namespaces: NamespaceListResolver
        }
    }, {
        path: ':namespace',
        component: AuthorDetailComponent,
        resolve: {
            namespace: NamespaceDetailResolver,
            repositories: RepositoryResolver
        }
    }];

@NgModule({
    imports: [
        RouterModule.forChild(routes)
    ],
    exports: [
        RouterModule
    ],
    providers: [
        NamespaceDetailResolver,
    	NamespaceListResolver,
        RepositoryResolver
    ]
})
export class AuthorsRoutingModule { }
