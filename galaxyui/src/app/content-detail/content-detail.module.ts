import { CommonModule } from '@angular/common';
import { NgModule }     from '@angular/core';

import { CardModule }                  from 'patternfly-ng/card/basic-card/card.module';
import { EmptyStateModule }            from 'patternfly-ng/empty-state/empty-state.module';
import { FilterModule }                from 'patternfly-ng/filter/filter.module';
import { ListModule }                  from 'patternfly-ng/list/basic-list/list.module';
import { PaginationModule }            from 'patternfly-ng/pagination/pagination.module';

import { TooltipModule }               from 'ngx-bootstrap/tooltip';

import { UtilitiesModule }             from '../utilities/utilities.module';

import { PageHeaderModule }            from '../page-header/page-header.module';
import { PageLoadingModule }           from '../page-loading/page-loading.module';
import { CardCloudPlatformsComponent } from './cards/cloud-platforms/cloud-platforms.component';
import { CardDependenciesComponent }   from './cards/dependencies/dependencies.component';
import { CardInfoComponent }           from './cards/info/card-info.component';
import { CardPlatformsComponent }      from './cards/platforms/platforms.component';
import { CardVersionsComponent }       from './cards/versions/versions.component';
import { ContentDetailComponent }      from './content-detail.component';
import { ContentDetailRoutingModule }  from './content-detail.routing.module';
import { ModuleUtilsComponent }        from './content/module-utils/module-utils.component';
import { ModulesComponent }            from './content/modules/modules.component';
import { PluginsComponent }            from './content/plugins/plugins.component';
import { RolesComponent }              from './content/roles/roles.component';
import { RepositoryComponent }         from './repository/repository.component';

import { SharedModule }                from '../shared/shared.module';

@NgModule({
    imports: [
        TooltipModule.forRoot(),
        PaginationModule,
        FilterModule,
        CommonModule,
        ContentDetailRoutingModule,
        EmptyStateModule,
        CardModule,
        PageLoadingModule,
        PageHeaderModule,
        ListModule,
        UtilitiesModule,
        SharedModule

    ],
    declarations: [
          ContentDetailComponent,
        RepositoryComponent,
        CardInfoComponent,
        CardPlatformsComponent,
        CardVersionsComponent,
        CardCloudPlatformsComponent,
        CardDependenciesComponent,
        ModulesComponent,
        RolesComponent,
        ModuleUtilsComponent,
        PluginsComponent,
    ]
})
export class ContentDetailModule { }
