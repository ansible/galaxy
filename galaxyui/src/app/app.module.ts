import { BrowserModule } from '@angular/platform-browser';

import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';

import { HttpClientModule, HttpClientXsrfModule } from '@angular/common/http';

import {
    AboutModalModule,
    ToastNotificationListModule,
    VerticalNavigationModule,
} from 'patternfly-ng';

import { BsDropdownModule, ModalModule, TooltipModule } from 'ngx-bootstrap';

import { NotificationService } from 'patternfly-ng';

import { AppComponent } from './app.component';

// Custom Modules
import { AppRoutingModule } from './app-routing.module';
import { AuthorsModule } from './authors/authors.module';

import { ContentDetailModule } from './content-detail/content-detail.module';
import { ExceptionPagesModule } from './exception-pages/exception-pages.module';
import { HomeModule } from './home/home.module';
import { LoginModule } from './login/login.module';
import { MyContentModule } from './my-content/my-content.module';
import { PreferencesModule } from './preferences/preferences.module';
import { VendorsModule } from './vendors/vendors.module';
import { UtilitiesModule } from './utilities/utilities.module';

// Custom Services
import { AuthService } from './auth/auth.service';
import { ApiRootService } from './resources/api-root/api-root.service';
import { CloudPlatformService } from './resources/cloud-platforms/cloud-platform.service';
import { ContentBlocksService } from './resources/content-blocks/content-blocks.service';
import { ContentSearchService } from './resources/content-search/content-search.service';
import { ContentTypeService } from './resources/content-types/content-type.service';
import { ContentService } from './resources/content/content.service';
import { EmailService } from './resources/emails/email.service';
import { ImportsService } from './resources/imports/imports.service';
import { EventLoggerService } from './resources/logger/event-logger.service';
import { NamespaceService } from './resources/namespaces/namespace.service';
import { PFBodyService } from './resources/pf-body/pf-body.service';
import { PlatformService } from './resources/platforms/platform.service';
import { PreferencesService } from './resources/preferences/preferences.service';
import { ProviderSourceService } from './resources/provider-namespaces/provider-source.service';
import { RepositoryService } from './resources/repositories/repository.service';
import { RepositoryImportService } from './resources/repository-imports/repository-import.service';
import { SurveyService } from './resources/survey/survey.service';
import { TagsService } from './resources/tags/tags.service';
import { UserService } from './resources/users/user.service';
import { UserNotificationService } from './resources/notifications/user-notification.service';
import {
    CollectionUploadService,
    CollectionListService,
    CollectionDetailService,
} from './resources/collections/collection.service';
import {
    RepoCollectionListService,
    RepoOrCollectionService,
} from './resources/combined/combined.service';

// import { MyImportsModule }            from './my-imports/my-imports.module';
// import { SearchModule }               from './search/search.module';
import { SharedModule } from './shared/shared.module';
import { UserNotificationsComponent } from './user-notifications/user-notifications.component';

@NgModule({
    declarations: [AppComponent, UserNotificationsComponent],
    imports: [
        HttpClientModule,
        HttpClientXsrfModule.withOptions({
            cookieName: 'csrftoken',
            headerName: 'X-CSRFToken',
        }),
        TooltipModule,
        BrowserModule,
        VerticalNavigationModule,
        BsDropdownModule.forRoot(),
        ModalModule.forRoot(),
        HomeModule,
        LoginModule,
        PreferencesModule,
        MyContentModule,
        ToastNotificationListModule,
        ContentDetailModule,
        ExceptionPagesModule,
        VendorsModule,
        AuthorsModule,
        AppRoutingModule,
        AboutModalModule,
        SharedModule,
        UtilitiesModule,
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
        ContentService,
        ApiRootService,
        PFBodyService,
        SurveyService,
        EmailService,
        EventLoggerService,
        PreferencesService,
        UserNotificationService,
        CollectionUploadService,
        CollectionListService,
        CollectionDetailService,
        RepoCollectionListService,
        RepoOrCollectionService,
    ],
    schemas: [CUSTOM_ELEMENTS_SCHEMA],
    bootstrap: [AppComponent],
})
export class AppModule {}
