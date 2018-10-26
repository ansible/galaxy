import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { SharedModule } from '../shared/shared.module';

import { ClipboardComponent } from './clipboard/clipboard.component';
import { ScoreComponent } from './score/score.component';
import { NotificationDrawerComponent } from './notification-drawer/notification-drawer.component';
import { NotificationDrawerModule } from 'patternfly-ng';
import { ActionModule } from 'patternfly-ng/';

@NgModule({
    imports: [
        CommonModule,
        TooltipModule,
        SharedModule,
        NotificationDrawerModule,
        ActionModule,
    ],
    declarations: [
        ClipboardComponent,
        ScoreComponent,
        NotificationDrawerComponent,
    ],
    exports: [ClipboardComponent, ScoreComponent, NotificationDrawerComponent],
})
export class UtilitiesModule {}
