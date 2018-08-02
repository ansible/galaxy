import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { Router }           from '@angular/router';

import { ActionConfig }     from 'patternfly-ng/action/action-config';

import { EventLoggerService } from '../../../resources/logger/event-logger.service';
import { Repository }         from '../../../resources/repositories/repository';

@Component({
    selector: 'author-detail-actions',
    templateUrl: './detail-actions.component.html',
    styleUrls: ['./detail-actions.component.less']
})
export class DetailActionsComponent implements OnInit {

    constructor(
        private router: Router,
        private eventLoggerService: EventLoggerService,
    ) {}

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
            primaryActions: [{
                id: 'more',
                title: 'View content',
                tooltip: 'View content details'
            }],
            moreActions: [{
                id: 'scmView',
                title: 'View SCM Repository',
                tooltip: 'Opens the SCM repository in new browser window or tab'
            }, {
                disabled: (!this.repository.issue_tracker_url) ? true : false,
                id: 'issueLog',
                title: 'Visit the Issue Log',
                tooltip: 'Opens the Issue Log in new browser window or tab'
            }],
        } as ActionConfig;
    }

    handleAction($event) {
        switch ($event.id) {
            case 'more':
                const url = `/${ this.repository.summary_fields['namespace']['name'] }/${ this.repository.name }`;
                this.eventLoggerService.logLink('View Content', url);
                this.router.navigate(['/', this.repository.summary_fields['namespace']['name'],
                    this.repository.name]);
                break;
            case 'scmView':
                this.eventLoggerService.logLink('View SCM Repository', this.repository.external_url);
                window.open(this.repository.external_url, '_blank');
                break;
            case 'issueLog':
                this.eventLoggerService.logLink('Visit the Issue Log', this.repository.issue_tracker_url);
                window.open(this.repository.issue_tracker_url, '_blank');
                break;
        }
    }
}
