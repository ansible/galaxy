import { NgModule }     from '@angular/core';
import { CommonModule } from '@angular/common';

import { EmptyStateModule }            from 'patternfly-ng/empty-state/empty-state.module'
import { CardModule }                  from 'patternfly-ng/card/card.module';
import { ListModule }                  from 'patternfly-ng/list/list.module';
import { PaginationModule }            from 'patternfly-ng/pagination/pagination.module';
import { FilterModule }                from 'patternfly-ng/filter/filter.module';

import { TooltipModule }               from 'ngx-bootstrap/tooltip';

import { ContentDetailRoutingModule }  from './content-detail.routing.module';
import { ContentDetailComponent }      from './content-detail.component';
import { RepositoryComponent }         from './repository/repository.component';
import { ModuleUtilsComponent }        from './content/module-utils/module-utils.component';
import { RolesComponent }              from './content/roles/roles.component';
import { ModulesComponent }            from './content/modules/modules.component';
import { PluginsComponent }            from './content/plugins/plugins.component';
import { CardInfoComponent }           from './cards/info/card-info.component';
import { CardPlatformsComponent }      from './cards/platforms/platforms.component';
import { CardVersionsComponent }       from './cards/versions/versions.component';
import { CardCloudPlatformsComponent } from './cards/cloud-platforms/cloud-platforms.component';
import { CardDependenciesComponent }   from './cards/dependencies/dependencies.component';
import { PageHeaderModule }            from '../page-header/page-header.module';
import { PageLoadingModule }           from '../page-loading/page-loading.module';


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
        PluginsComponent
    ]
})
export class ContentDetailModule { }
