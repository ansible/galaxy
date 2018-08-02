import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    TemplateRef,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';

import { Action }           from 'patternfly-ng/action/action';
import { ActionConfig }     from 'patternfly-ng/action/action-config';

import { EventLoggerService } from '../../../../../resources/logger/event-logger.service';
import { Repository }         from '../../../../../resources/repositories/repository';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-repository-action',
    templateUrl: './action.component.html',
    styleUrls: ['./action.component.less']
})
export class NamespaceRepositoryActionComponent implements OnInit {

    @ViewChild('importButtonTemplate') public buttonTemplate: TemplateRef<any>;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    @Output() handleAction = new EventEmitter<any>();

    _repository: Repository;
    actionConfig: ActionConfig;

    constructor(
        private eventLoggerService: EventLoggerService,
    ) {}

    ngOnInit(): void {
        let importing = false;
        if (this.repository['latest_import'] &&
            (this.repository['latest_import']['state'] === 'PENDING' ||
                this.repository['latest_import']['state'] === 'RUNNING')) {
            importing = true;
        }
        this.actionConfig = {
            primaryActions: [{
                id: 'import',
                title: 'Import',
                tooltip: 'Import Repository',
                template: this.buttonTemplate,
                disabled: importing
            }],
            moreActions: [{
                id: 'delete',
                title: 'Delete',
                tooltip: 'Delete Repository'
            }],
            moreActionsDisabled: false,
            moreActionsVisible: !importing
        } as ActionConfig;
    }

    handleListAction($event: Action) {
        const event = {
            id: $event.id,
            item: this.repository
        };

        this.eventLoggerService.logButton($event.title);
        this.handleAction.emit(event);
    }
}
