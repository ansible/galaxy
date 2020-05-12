import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ContentFormat } from '../enums/format';
import { CollectionDetail } from '../resources/collections/collection';
import { CollectionImport } from '../resources/imports/import';

import { Repository } from '../resources/repositories/repository';
import { Content } from '../resources/content/content';
import { Namespace } from '../resources/namespaces/namespace';

@Component({
    selector: 'app-content-detail-loader',
    template: `
        <app-repo-detail
            *ngIf="contentType === ContentFormat.repository"
            [repository]="repository"
            [content]="content"
            [namespace]="namespace"
        ></app-repo-detail>
        <app-collection-detail
            *ngIf="contentType === ContentFormat.collection"
            [collection]="collection"
        ></app-collection-detail>
    `,
    styles: [''],
})
export class DetailLoaderComponent implements OnInit {
    componentName = 'DetailLoaderComponent';
    contentType: ContentFormat;
    repository: Repository;
    collection: CollectionDetail;
    content: Content[];
    namespace: Namespace;

    ContentFormat: typeof ContentFormat = ContentFormat;

    constructor(private route: ActivatedRoute) {}
    ngOnInit() {
        this.route.data.subscribe(data => {
            this.contentType = data.contentType['type'];
            this.collection = data.contentType['data']['collection'];
            this.repository = data.contentType['data']['repository'];
            this.content = data.contentType['data']['content'];
            this.namespace = data.contentType['data']['namespace'];
        });
    }
}
