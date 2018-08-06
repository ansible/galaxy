import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { AccessDeniedComponent } from './access-denied/access-denied.component';
import { NotFoundComponent } from './not-found/not-found.component';

const exceptionPagesRoutes: Routes = [
    {
        path: 'access-denied',
        component: AccessDeniedComponent,
    },
    {
        path: 'not-found',
        component: NotFoundComponent,
    },
];

@NgModule({
    imports: [RouterModule.forChild(exceptionPagesRoutes)],
    exports: [RouterModule],
})
export class ExceptionPagesRoutingModule {}
