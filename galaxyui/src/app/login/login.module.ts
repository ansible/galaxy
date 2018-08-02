import {
    NgModule
} from '@angular/core';

import {
    LoginComponent
} from './login.component';

import {
    LoginRoutingModule
} from './login.routing.module';

import {
    CardModule
} from 'patternfly-ng/card/basic-card/card.module';

import { SharedModule } from '../shared/shared.module';

@NgModule({
    declarations: [
        LoginComponent
    ],
    imports: [
        CardModule,
        LoginRoutingModule,
        SharedModule
    ],
    providers: []
})
export class LoginModule { }
