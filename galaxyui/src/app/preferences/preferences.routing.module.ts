import { NgModule } from '@angular/core';

import { RouterModule, Routes } from '@angular/router';

import { PreferencesComponent } from './preferences.component';

const preferencesRoutes: Routes = [
    {
        path: 'me/preferences',
        component: PreferencesComponent,
    },
];

@NgModule({
    imports: [RouterModule.forChild(preferencesRoutes)],
    exports: [RouterModule],
})
export class PreferencesRoutingModule {}
