import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { CardModule } from 'patternfly-ng/card/basic-card/card.module';
import { EmptyStateModule } from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule } from 'patternfly-ng/filter/filter.module';
import { ListModule } from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule } from 'patternfly-ng/pagination/pagination.module';

import { TooltipModule } from 'ngx-bootstrap/tooltip';

import { UtilitiesModule } from '../utilities/utilities.module';

import { SharedModule } from '../shared/shared.module';
import { CardCloudPlatformsComponent } from './cards/cloud-platforms/cloud-platforms.component';
import { CardCommunitySurveyComponent } from './cards/survey/community-survey.component';

import { CardDependenciesComponent } from './cards/dependencies/dependencies.component';
import { CardInfoComponent } from './cards/info/card-info.component';
import { CardPlatformsComponent } from './cards/platforms/platforms.component';
import { QualityDetailsComponent } from './cards/quality-details/quality-details.component';
import { CardVersionsComponent } from './cards/versions/versions.component';
import { CardCollectionContentComponent } from './cards/collection-content/collection-content.component';

import { RepositoryDetailComponent } from './repository-detail/repository-detail.component';
import { CollectionDetailComponent } from './collection-detail/collection-detail.component';
import { ContentDetailRoutingModule } from './content-detail.routing.module';
import { ModuleUtilsComponent } from './content/module-utils/module-utils.component';
import { ModulesComponent } from './content/modules/modules.component';
import { PluginsComponent } from './content/plugins/plugins.component';
import { RolesComponent } from './content/roles/roles.component';
import { ContentHeaderComponent } from './content-header/content-header.component';
import { DetailLoaderComponent } from './detail-loader.component';

import { ScoreBarComponent } from './shared/score-bar/score-bar.component';

@NgModule({
    imports: [
        TooltipModule.forRoot(),
        PaginationModule,
        FilterModule,
        CommonModule,
        ContentDetailRoutingModule,
        EmptyStateModule,
        CardModule,

        SharedModule,
        ListModule,
        UtilitiesModule,
    ],
    declarations: [
        RepositoryDetailComponent,
        CollectionDetailComponent,
        ContentHeaderComponent,
        CardInfoComponent,
        CardPlatformsComponent,
        CardVersionsComponent,
        CardCloudPlatformsComponent,
        CardDependenciesComponent,
        CardCommunitySurveyComponent,
        CardCollectionContentComponent,
        ModulesComponent,
        RolesComponent,
        ModuleUtilsComponent,
        PluginsComponent,
        ScoreBarComponent,
        QualityDetailsComponent,
        DetailLoaderComponent,
    ],
})
export class ContentDetailModule {}
