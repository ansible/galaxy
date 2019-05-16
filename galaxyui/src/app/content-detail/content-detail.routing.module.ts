import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
    // ':namespace/:repository/:content_name' and ':namespace/:repository/ moved
    // to app-routing.module
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: [],
})
export class ContentDetailRoutingModule {}
