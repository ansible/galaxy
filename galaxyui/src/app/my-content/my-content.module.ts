import { NgModule }     from '@angular/core';
import { CommonModule } from '@angular/common';
import {
    FormsModule,
    ReactiveFormsModule
}                       from '@angular/forms';

import { MyContentRoutingModule } from './my-content.routing.module';

import {
    BsDropdownConfig,
    BsDropdownModule
} from 'ngx-bootstrap';


import { ActionModule }     from 'patternfly-ng/action/action.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }     from 'patternfly-ng/filter/filter.module';
import { ToolbarModule }    from 'patternfly-ng/toolbar/toolbar.module';
import { ListModule }       from 'patternfly-ng/list/list.module';
import { ModalModule }      from 'patternfly-ng';

import { NotificationService }   from 'patternfly-ng/notification/notification-service/notification.service';
import { NamespaceService }      from '../resources/namespaces/namespace.service';
import { UserService }           from '../resources/users/user.service';
import { ProviderSourceService } from '../resources/provider-namespaces/provider-source.service';
import { RepositoryService }     from '../resources/respositories/repository.service';

import { NamespaceListComponent }             from './namespace-list/namespace-list.component';
import { NamespaceDetailComponent }           from './namespace-detail/namespace-detail.component';
import { RepositoriesContentComponent }       from './namespace-list/content/repositories-content/repositories-content.component';
import { OwnersContentComponent }             from './namespace-list/content/owners-content/owners-content.component';
import { ProviderNamespacesContentComponent } from './namespace-list/content/provider-namespaces-content/provider-namespaces-content.component';
import { AddRepositoryModalComponent }        from './add-repository-modal/add-repository-modal.component';


@NgModule({
    entryComponents: [
        AddRepositoryModalComponent
    ],
    declarations: [
        NamespaceListComponent,
        NamespaceDetailComponent,
        RepositoriesContentComponent,
        OwnersContentComponent,
        ProviderNamespacesContentComponent,
        AddRepositoryModalComponent
    ],
    imports: [
        ActionModule,
        BsDropdownModule.forRoot(), //TODO forRoot?
        ModalModule,
        CommonModule,
        EmptyStateModule,
        FilterModule,
        FormsModule,
        ReactiveFormsModule,
        ToolbarModule,
        ListModule,
        MyContentRoutingModule
    ],
    providers: [
        BsDropdownConfig,
        NotificationService,
        NamespaceService,
        UserService,
        ProviderSourceService,
        RepositoryService
    ]
})
export class MyContentModule {
}
