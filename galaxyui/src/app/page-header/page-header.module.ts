import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';

import { PageHeaderComponent } from './page-header.component';

@NgModule({
    imports: [RouterModule, CommonModule],
    declarations: [PageHeaderComponent],
    exports: [PageHeaderComponent],
})
export class PageHeaderModule {}
