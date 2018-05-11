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
import { SearchModule }               from './search/search.module';
import { UserNotificationsComponent } from './user-notifications/user-notifications.component';
import { AuthorsModule }              from './authors/authors.module';
import { ContentDetailModule }        from './content-detail/content-detail.module';
import { AuthService }                from './auth/auth.service';
import { NamespaceService }           from './resources/namespaces/namespace.service';
import { UserService }                from './resources/users/user.service';
import { RepositoryService }          from './resources/repositories/repository.service';
import { ProviderSourceService }      from './resources/provider-namespaces/provider-source.service';
import { RepositoryImportService }    from './resources/repository-imports/repository-import.service';
import { ImportsService }             from './resources/imports/imports.service';
import { ContentBlocksService }       from './resources/content-blocks/content-blocks.service';
import { ContentSearchService }       from './resources/content-search/content-search.service';
import { PlatformService }            from './resources/platforms/platform.service';
import { ContentTypeService }         from './resources/content-types/content-type.service';
import { CloudPlatformService }       from './resources/cloud-platforms/cloud-platform.service';
import { TagsService }                from './resources/tags/tags.service';
import { ContentService }             from './resources/content/content.service';
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
        SearchModule,
        ModalModule,
        ContentDetailModule,
        AuthorsModule,
        AppRoutingModule
    ],
    providers: [
        AuthService,
        CloudPlatformService,
        ContentBlocksService,
        ContentSearchService,
        ContentTypeService,
        ImportsService,
        NamespaceService,
        NotificationService,
        PlatformService,
        ProviderSourceService,
        RepositoryImportService,
        RepositoryService,
        TagsService,
        UserService,
        ContentService
    ],
    schemas: [
        CUSTOM_ELEMENTS_SCHEMA
    ],
    bootstrap: [AppComponent]
})
export class AppModule {}
