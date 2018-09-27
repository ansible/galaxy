import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { SharedModule } from '../shared/shared.module';

import { ClipboardComponent } from './clipboard/clipboard.component';
import { ScoreComponent } from './score/score.component';

@NgModule({
    imports: [CommonModule, TooltipModule, SharedModule],
    declarations: [ClipboardComponent, ScoreComponent],
    exports: [ClipboardComponent, ScoreComponent],
})
export class UtilitiesModule {}
