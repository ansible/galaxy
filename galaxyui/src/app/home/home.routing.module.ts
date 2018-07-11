import {
    NgModule
} from '@angular/core';

import {
    RouterModule,
    Routes
} from '@angular/router';

import {
    HomeComponent
} from './home.component';

import {
    ContentBlockResolver,
    VendorListResolver
} from './home.resolver.service';

const homeRoutes: Routes = [
    {
        path: 'home',
        component: HomeComponent,
        resolve: {
            vendors: VendorListResolver,
            contentBlocks: ContentBlockResolver
        }
    }
];

@NgModule({
    imports: [
        RouterModule.forChild(homeRoutes)
    ],
    exports: [
        RouterModule,
    ],
    providers: [
        VendorListResolver,
        ContentBlockResolver
    ]
})
export class HomeRoutingModule { }
