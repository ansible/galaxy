import { NgModule }                   from '@angular/core';
import { RouterModule, Routes }       from '@angular/router';

import { ExperimentComponent }              from './experiment.component';

const experimentRoutes: Routes = [
    {
        path: 'experiment',
        component: ExperimentComponent
    }
];

@NgModule({
    imports: [
        RouterModule.forChild(experimentRoutes)
    ],
    exports: [
        RouterModule,
    ],
    providers: []
})
export class ExperimentRoutingModule { }
