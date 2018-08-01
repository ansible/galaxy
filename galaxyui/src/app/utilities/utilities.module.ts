import { CommonModule }    from '@angular/common';
import { NgModule }        from '@angular/core';

import { TooltipModule }       from 'ngx-bootstrap/tooltip';

import { ClipboardComponent }  from './clipboard/clipboard.component';

import { SharedModule }        from '../shared/shared.module';

@NgModule({
    imports: [
        CommonModule,
        TooltipModule,
        SharedModule
    ],
    declarations: [
        ClipboardComponent
    ],
    exports: [
        ClipboardComponent
    ]
})
export class UtilitiesModule { }
