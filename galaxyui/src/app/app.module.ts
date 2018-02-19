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

import { AppComponent }               from './app.component';
import { UserNotificationsComponent } from './user-notifications/user-notifications.component';
import { AppRoutingModule }           from './app-routing.module';
import { HomeModule }                 from './home/home.module';
import { MyContentModule }            from './my-content/my-content.module';
import { ExperimentModule }           from './experiment/experiment.module';
import { AuthService }                from './auth/auth.service';
import { NotificationService }        from 'patternfly-ng/notification/notification-service/notification.service';
import { NotificationModule }         from 'patternfly-ng/notification/notification.module';

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
        HomeModule,
        MyContentModule,
        ExperimentModule,
        ModalModule,
        AppRoutingModule
    ],
    providers: [
        AuthService,
        NotificationService
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ],
    bootstrap: [AppComponent]
})
export class AppModule {
}
