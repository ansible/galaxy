import {
    BrowserModule
} from '@angular/platform-browser';

import {
    NgModule,
    CUSTOM_ELEMENTS_SCHEMA
} from '@angular/core';

import {
    HttpClientModule,
    HttpClientXsrfModule
} from '@angular/common/http';

import {
    NavigationModule,
    ModalModule
} from 'patternfly-ng';

import {
    BsDropdownModule,
    ModalModule as BsModalModule
} from 'ngx-bootstrap';

import { NotificationModule }         from 'patternfly-ng/notification/notification.module';
import { NotificationService }        from 'patternfly-ng/notification/notification-service/notification.service';
import { CardModule }                 from 'patternfly-ng/card/card.module';

import { HomeModule }                 from './home/home.module';
import { LoginModule }                from './login/login.module';
import { MyContentModule }            from './my-content/my-content.module';
import { MyImportsModule }            from './my-imports/my-imports.module';
import { UserNotificationsComponent } from './user-notifications/user-notifications.component';

import { AuthService }                from './auth/auth.service';
import { NamespaceService }           from './resources/namespaces/namespace.service';
import { UserService }                from './resources/users/user.service';
import { RepositoryService }          from './resources/respositories/repository.service';
import { ProviderSourceService }      from './resources/provider-namespaces/provider-source.service';
import { RepositoryImportService }    from './resources/repository-imports/repository-import.service';
import { ImportsService }             from './resources/imports/imports.service';
import { ContentBlocksService }       from './resources/content-blocks/content-blocks.service';
import { AppRoutingModule }           from './app-routing.module';
import { AppComponent }               from './app.component';


@NgModule({
    declarations: [
        AppComponent,
        UserNotificationsComponent
    ],
    imports: [
        HttpClientModule,
        HttpClientXsrfModule.withOptions({
            cookieName: 'csrftoken',
            headerName: 'X-CSRFToken',
        }),
        BrowserModule,
        NavigationModule,
        BsDropdownModule.forRoot(),
        BsModalModule.forRoot(),
        NotificationModule,
        CardModule,
        HomeModule,
        LoginModule,
        MyContentModule,
        MyImportsModule,
        ModalModule,
        AppRoutingModule
    ],
    providers: [
        AuthService,
        NotificationService,
        NamespaceService,
        UserService,
        ProviderSourceService,
        RepositoryService,
        RepositoryImportService,
        ImportsService,
        ContentBlocksService
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ],
    bootstrap: [AppComponent]
})
export class AppModule {}
