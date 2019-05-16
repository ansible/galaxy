import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ContentFormat } from '../enums/format';

@Component({
    selector: 'app-content-detail-loader',
    template:
        '<app-repo-detail *ngIf="contentType === ContentFormat.repository"></app-repo-detail>' +
        '<app-collection-detail *ngIf="contentType === ContentFormat.collection"></app-collection-detail>',
    styles: [''],
})
export class DetailLoaderComponent implements OnInit {
    componentName = 'DetailLoaderComponent';
    contentType: ContentFormat;
    ContentFormat: typeof ContentFormat = ContentFormat;

    constructor(private route: ActivatedRoute) {}
    ngOnInit() {
        this.route.data.subscribe(data => {
            this.contentType = data.contentType;
        });
    }
}
