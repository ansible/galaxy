/* (c) 2012-2018, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
 */

import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { ImportListComponent } from './import-list/import-list.component';
import { UserNamespacesResolver } from './import-list/import-list.resolver.service';

const myImportRoutes: Routes = [
    {
        path: '',
        component: ImportListComponent,
        resolve: {
            namespaces: UserNamespacesResolver,
        },
        canActivate: [AuthService],
    },
];

@NgModule({
    imports: [RouterModule.forChild(myImportRoutes)],
    exports: [RouterModule],
    providers: [UserNamespacesResolver],
})
export class MyImportsRoutingModule {}
