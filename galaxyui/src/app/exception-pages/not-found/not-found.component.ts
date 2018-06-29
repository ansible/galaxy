import {
    Component,
    OnInit,
    TemplateRef,
    ViewEncapsulation
} from '@angular/core';

import {
    ActivatedRoute,
    Router
} from '@angular/router';

import {
    EmptyStateConfig
} from 'patternfly-ng/empty-state';

import {
    ActionConfig,
    Action
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

    pageTitle = '<i class="fa fa-frown-o"></i> Page Not Found';
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
