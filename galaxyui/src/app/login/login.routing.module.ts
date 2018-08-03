import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { LoginComponent } from './login.component';

const loginRoutes: Routes = [
    {
        path: 'login',
        component: LoginComponent,
    },
];

@NgModule({
    imports: [RouterModule.forChild(loginRoutes)],
    exports: [RouterModule],
    providers: [],
})
export class LoginRoutingModule {}
