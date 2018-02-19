import {
    Component,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'experiment',
    templateUrl: './experiment.component.html',
    styleUrls: ['./experiment.component.less']
})
export class ExperimentComponent implements OnInit {

    constructor() {}

    ngOnInit(): void {
    }

}
