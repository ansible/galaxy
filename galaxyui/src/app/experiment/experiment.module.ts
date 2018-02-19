import { NgModule }                from '@angular/core';
import { CommonModule }            from '@angular/common';
import { ExperimentComponent }     from './experiment.component';
import { ExperimentRoutingModule } from './experiment.routing.module';

@NgModule({
    imports: [
        CommonModule,
        ExperimentRoutingModule
    ],
    declarations: [ExperimentComponent]
})
export class ExperimentModule {
}
