import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { Action } from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';

import { Email } from '../../resources/emails/email';

@Component({
    selector: 'app-email-action',
    templateUrl: './email-action.component.html',
    styleUrls: ['./email-action.component.less'],
})
export class EmailActionComponent implements OnInit {
    constructor() {}

    actionConfig: ActionConfig;

    @Input()
    email: Email;

    @Output()
    handleAction = new EventEmitter<any>();

    ngOnInit() {
        this.actionConfig = {
            moreActions: [
                {
                    id: 'delete',
                    title: 'Delete',
                    tooltip: 'Delete Email',
                    disabled: this.email.primary,
                },
                {
                    id: 'edit',
                    title: 'Edit',
                    tooltip: 'Edit Email',
                    disabled: this.email.verified || this.email.primary,
                },
            ] as Action[],
        } as ActionConfig;
    }

    handleEmailAction($event: Action) {
        const event = {
            id: $event.id,
            email: this.email,
        };

        this.handleAction.emit(event);
    }
}
