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
    selector: 'app-access-denied',
    templateUrl: './access-denied.component.html',
    styleUrls: ['./access-denied.component.less']
})
export class AccessDeniedComponent implements OnInit {

    constructor(
        private router: Router
    ) {}

    pageTitle = 'Access Denied';
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
            info: 'You do not have access to the requested page. Choose one of the navigation options on the left, ' +
                'or click the Home button below, to visit the home page',
            title: 'Access Denied'
        } as EmptyStateConfig;
    }

    handleActionClicked($event: Action) {
        this.router.navigate(['/home']);
    }
}
