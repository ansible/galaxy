import {
    NgModule
} from '@angular/core';

import {
    RouterModule,
    Routes
} from '@angular/router';

import {
    ExploreComponent
} from './explore.component';


const exploreRoutes: Routes = [
    {
        path: 'explore',
        component: ExploreComponent
    }
];

@NgModule({
    imports: [
        RouterModule.forChild(exploreRoutes)
    ],
    exports: [
        RouterModule,
    ],
    providers: []
})
export class ExploreRoutingModule { }
