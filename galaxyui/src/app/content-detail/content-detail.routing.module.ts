import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { CollectionResolver } from './content-detail.resolver.service';

const routes: Routes = [
    // ':namespace/:repository/:content_name' and ':namespace/:repository/ moved
    // to app-routing.module
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: [CollectionResolver],
})
export class ContentDetailRoutingModule {}
