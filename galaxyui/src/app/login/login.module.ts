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
} from 'patternfly-ng/card/card.module';

@NgModule({
    declarations: [
        LoginComponent
    ],
    imports: [
        CardModule,
        LoginRoutingModule
    ],
    providers: []
})
export class LoginModule { }
