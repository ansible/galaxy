import {
	NgModule,
	CUSTOM_ELEMENTS_SCHEMA
} from '@angular/core';

import { HomeComponent }        from './home.component';
import { HomeRoutingModule }    from './home.routing.module';

import {
	CardModule
} from 'patternfly-ng/card/card.module';

import { PageHeaderModule }     from '../page-header/page-header.module';
import { PageLoadingModule }    from '../page-loading/page-loading.module';

@NgModule({
    declarations: [
        HomeComponent
    ],
    imports: [
    	CardModule,
    	PageHeaderModule,
    	PageLoadingModule,
        HomeRoutingModule
    ],
    providers: [],
	schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class HomeModule { }
