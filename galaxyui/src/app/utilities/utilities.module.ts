import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

import { ClipboardComponent } from './clipboard/clipboard.component';
import { ScoreComponent } from './score/score.component';
import { NotificationDrawerComponent } from './notification-drawer/notification-drawer.component';
import { CollectionListItemComponent } from './collection-list-item/collection-list-item.component';

import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { SharedModule } from '../shared/shared.module';
import { NotificationDrawerModule } from 'patternfly-ng';
import { ActionModule } from 'patternfly-ng/';

@NgModule({
    imports: [
        CommonModule,
        TooltipModule,
        SharedModule,
        NotificationDrawerModule,
        ActionModule,
        RouterModule,
    ],
    declarations: [
        ClipboardComponent,
        ScoreComponent,
        NotificationDrawerComponent,
        CollectionListItemComponent,
    ],
    exports: [
        ClipboardComponent,
        ScoreComponent,
        NotificationDrawerComponent,
        CollectionListItemComponent,
    ],
})
export class UtilitiesModule {}
