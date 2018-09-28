import { Component, Input, OnInit } from '@angular/core';

import { Router } from '@angular/router';

import { ActionConfig } from 'patternfly-ng/action/action-config';

import { Repository } from '../../../resources/repositories/repository';

@Component({
    selector: 'author-detail-actions',
    templateUrl: './detail-actions.component.html',
    styleUrls: ['./detail-actions.component.less'],
})
export class DetailActionsComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'DetailActionsComponent';

    constructor(private router: Router) {}

    _repository: Repository;
    actionConfig: ActionConfig;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    ngOnInit() {
        this.actionConfig = {
            primaryActions: [
                {
                    id: 'more',
                    title: 'View content',
                    tooltip: 'View content details',
                },
            ],
            moreActions: [
                {
                    id: 'scmView',
                    title: 'View SCM Repository',
                    tooltip: 'Opens the SCM repository in new browser window or tab',
                },
                {
                    disabled: this._repository.issue_tracker_url ? true : false,
                    id: 'issueLog',
                    title: 'Visit the Issue Log',
                    tooltip: 'Opens the Issue Log in new browser window or tab',
                },
            ],
        } as ActionConfig;
    }

    handleAction($event) {
        switch ($event.id) {
            case 'more':
                this.router.navigate(['/', this.repository.summary_fields['namespace']['name'], this.repository.name]);
                break;
            case 'scmView':
                window.open(this.repository.external_url, '_blank');
                break;
            case 'issueLog':
                window.open(this.repository.issue_tracker_url, '_blank');
                break;
        }
    }
}
