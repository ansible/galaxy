import { NgModule } from '@angular/core';

import { CommonModule } from '@angular/common';

import { EmailActionComponent } from './email-action/email-action.component';
import { PreferencesComponent } from './preferences.component';
import { PreferencesRoutingModule } from './preferences.routing.module';

import { SharedModule } from '../shared/shared.module';

import { ActionModule } from 'patternfly-ng/action/action.module';
import { CardModule } from 'patternfly-ng/card/basic-card/card.module';
import { InlineCopyModule } from 'patternfly-ng/copy/inline-copy/inline-copy.module';
import { ListModule } from 'patternfly-ng/list/basic-list/list.module';

import { FormsModule } from '@angular/forms';

@NgModule({
    imports: [
        CommonModule,
        PreferencesRoutingModule,
        SharedModule,
        CardModule,
        ListModule,
        InlineCopyModule,
        FormsModule,
        ActionModule,
    ],
    declarations: [PreferencesComponent, EmailActionComponent],
})
export class PreferencesModule {}
