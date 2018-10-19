import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output,
    TemplateRef,
    ViewChild,
    ViewEncapsulation,
} from '@angular/core';

import { Action } from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';

import { Repository } from '../../../../../resources/repositories/repository';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-repository-action',
    templateUrl: './action.component.html',
    styleUrls: ['./action.component.less'],
})
export class NamespaceRepositoryActionComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'NamespaceRepositoryActionComponent';

    @ViewChild('importButtonTemplate')
    public buttonTemplate: TemplateRef<any>;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }

    get repository(): Repository {
        return this._repository;
    }

    @Output()
    handleAction = new EventEmitter<any>();

    _repository: Repository;
    actionConfig: ActionConfig;

    constructor() {}

    ngOnInit(): void {
        let importing = false;
        if (
            this.repository['latest_import'] &&
            (this.repository['latest_import']['state'] === 'PENDING' ||
                this.repository['latest_import']['state'] === 'RUNNING')
        ) {
            importing = true;
        }
        this.actionConfig = {
            primaryActions: [
                {
                    id: 'import',
                    title: 'Import',
                    tooltip: 'Import Repository',
                    template: this.buttonTemplate,
                    disabled: importing,
                },
            ],
            moreActions: [
                {
                    id: 'delete',
                    title: 'Delete',
                    tooltip: 'Delete Repository',
                },
                {
                    id: 'deprecate',
                    title: 'Deprecate',
                    tooltip: 'Deprecate this Repository',
                    visible: !this.repository.deprecated,
                },
                {
                    id: 'undeprecate',
                    title: 'Un-Deprecate',
                    tooltip: 'Un-Deprecate this Repository',
                    visible: this.repository.deprecated,
                },
            ],
            moreActionsDisabled: false,
            moreActionsVisible: !importing,
        } as ActionConfig;
    }

    handleListAction($event: Action) {
        const event = {
            id: $event.id,
            item: this.repository,
        };
        this.handleAction.emit(event);
    }
}
