import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { PageLoadingComponent } from './page-loading.component';

@NgModule({
    imports: [CommonModule],
    declarations: [PageLoadingComponent],
    exports: [PageLoadingComponent],
})
export class PageLoadingModule {}
