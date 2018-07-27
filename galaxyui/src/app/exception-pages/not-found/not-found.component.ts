import {
    Component,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

import {
    Router
} from '@angular/router';

import {
    EmptyStateConfig
} from 'patternfly-ng/empty-state';

import {
    Action,
    ActionConfig
} from 'patternfly-ng/action';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'app-not-found',
    templateUrl: './not-found.component.html',
    styleUrls: ['./not-found.component.less']
})
export class NotFoundComponent implements OnInit {

    constructor(
        private router: Router
    ) {}

    pageTitle = 'Page Not Found';
    pageIcon = 'fa fa-frown-o';
    actionConfig: ActionConfig;
    emptyStateConfig: EmptyStateConfig;

    ngOnInit(): void {
        this.actionConfig = {
            primaryActions: [{
                id: 'home',
                title: 'Home',
                tooltip: 'View the home page'
            }]
        } as ActionConfig;

        this.emptyStateConfig = {
            actions: this.actionConfig,
            iconStyleClass: 'fa fa-frown-o',
            info: 'Well this is embarrassing. The page you requested could not be found. ' +
                'Choose one of the navigation options on the left, or click the Home button ' +
                'below, to visit the home page',
            title: 'Page Not Found'
        } as EmptyStateConfig;
    }

    handleActionClicked($event: Action) {
        this.router.navigate(['/home']);
    }
}
