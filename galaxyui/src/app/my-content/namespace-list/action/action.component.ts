import { Component, EventEmitter, Input, OnInit, Output, TemplateRef, ViewChild, ViewEncapsulation } from '@angular/core';

import { Action } from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';

import { AuthService } from '../../../auth/auth.service';
import { Namespace } from '../../../resources/namespaces/namespace';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-action',
    templateUrl: './action.component.html',
    styleUrls: ['./action.component.less'],
})
export class NamespaceActionComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'NamespaceActionComponent';

    @ViewChild('addContentButtonTemplate')
    public buttonTemplate: TemplateRef<any>;

    @Input()
    set namespace(data: Namespace) {
        this._namespace = data;
    }

    get namespace(): Namespace {
        return this._namespace;
    }

    @Output()
    handleAction = new EventEmitter<any>();

    _namespace: Namespace;
    actionConfig: ActionConfig;

    constructor(private authService: AuthService) {}

    ngOnInit(): void {
        const provider_namespaces = this.namespace['summary_fields']['provider_namespaces'];

        let primaryTooltip = 'Add yor Ansible content repositories';
        if (!this.namespace.active) {
            primaryTooltip = 'Namespace is disabled';
        }
        if (!provider_namespaces.length) {
            primaryTooltip = 'Missing provider namespaces';
        }

        this.actionConfig = {
            primaryActions: [
                {
                    id: 'addContent',
                    title: 'Add Content',
                    styleClass: 'btn-primary',
                    tooltip: primaryTooltip,
                    template: this.buttonTemplate,
                    disabled: !this.namespace.active || !provider_namespaces.length,
                },
            ] as Action[],
            moreActions: [
                {
                    id: 'enableNamespace',
                    title: 'Enable',
                    styleClass: 'btn-default',
                    tooltip: 'Enable namespace',
                    visible: !this.namespace.active,
                },
                {
                    id: 'editNamespaceProps',
                    title: 'Edit Properties',
                    tooltip: 'Edit namespace properties',
                },
                {
                    id: 'disableNamespace',
                    title: 'Disable',
                    tooltip: 'Disable namespace',
                    visible: this.namespace.active,
                },
                {
                    id: 'deleteNamespace',
                    title: 'Delete',
                    tooltip: 'Delete namespace',
                    visible: this.authService.meCache.staff,
                },
            ] as Action[],
            moreActionsDisabled: false,
            moreActionsVisible: true,
            moreActionsStyleClass: '',
        } as ActionConfig;
    }

    handleListAction($event: Action) {
        const event = {
            id: $event.id,
            item: this.namespace,
        };
        this.handleAction.emit(event);
    }
}
