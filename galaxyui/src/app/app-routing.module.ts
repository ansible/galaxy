import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { NotFoundComponent }    from './exception-pages/not-found/not-found.component';

const appRoutes: Routes = [
    {
        path: '',
        redirectTo: '/home',
        pathMatch: 'full'
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
