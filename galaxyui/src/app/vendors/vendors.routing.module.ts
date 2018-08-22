import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { VendorListResolver } from './vendors.resolver.service';

import { VendorsComponent } from './vendors.component';

const routes: Routes = [
    {
        path: 'partners',
        component: VendorsComponent,
        resolve: {
            vendors: VendorListResolver,
        },
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: [VendorListResolver],
})
export class VendorsRoutingModule {}
