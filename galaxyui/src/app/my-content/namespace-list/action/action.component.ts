import {
    Component,
    EventEmitter,
    Input,
    Output,
    OnInit,
    TemplateRef,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';

import { Action }           from 'patternfly-ng/action/action';
import { ActionConfig }     from 'patternfly-ng/action/action-config';

import { Namespace }        from '../../../resources/namespaces/namespace';
import { AuthService }      from '../../../auth/auth.service';


@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'namespace-action',
    templateUrl: './action.component.html',
    styleUrls: ['./action.component.less']
})
export class NamespaceActionComponent implements OnInit {

    @ViewChild('addContentButtonTemplate') public buttonTemplate: TemplateRef<any>;

    @Input()
    set namespace(data:Namespace) {
        this._namespace = data;
    }

    get namespace(): Namespace {
        return this._namespace;
    }

    @Output() handleAction = new EventEmitter<any>();

    _namespace: Namespace;
    actionConfig: ActionConfig;

    constructor(
        private authService: AuthService
    ) {}

    ngOnInit(): void {
        let provider_namespaces = this.namespace['summary_fields']['provider_namespaces'];
        this.actionConfig = {
            primaryActions: [{
                id: 'addContent',
                title: 'Add Content',
                styleClass: 'btn-primary',
                tooltip: 'Add roles, modules, APBs and other content from repositories',
                template: this.buttonTemplate,
                disabled: !this.namespace.active || !provider_namespaces.length
            }] as Action[],
            moreActions: [{
                id: 'enableNamespace',
                title: 'Enable',
                styleClass: 'btn-default',
                tooltip: 'Enable namespace',
                visible: !this.namespace.active
            },
            {
                id: 'editNamespaceProps',
                title: 'Edit Properties',
                tooltip: 'Edit namespace properties'
            },
            {
                id: 'disableNamespace',
                title: 'Disable',
                tooltip: 'Disable namespace',
                visible: this.namespace.active
            }, {
                id: 'deleteNamespace',
                title: 'Delete',
                tooltip: 'Delete namespace',
                visible: this.authService.meCache.staff
            }] as Action[],
            moreActionsDisabled: false,
            moreActionsVisible: true,
            moreActionsStyleClass: ''
        } as ActionConfig;
        //console.log(this.actionConfig);
    }

    handleListAction($event: Action) {
        let event = {
            id: $event.id,
            item: this.namespace
        }
        this.handleAction.emit(event);
    }
}
