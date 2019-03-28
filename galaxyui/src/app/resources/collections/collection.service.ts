import { HttpClient, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng';
import {
    CollectionUpload,
    CollectionList,
    CollectionDetail,
} from './collection';

import { ServiceBase } from '../base/service-base';
import { GenericQuery } from '../base/generic-query';
import { Observable } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable()
export class CollectionUploadService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(http, notificationService, '/api/v2/collections', 'collection');
    }

    upload(artifact: CollectionUpload): Observable<any> {
        const formData = new FormData();
        formData.append('file', artifact.file);
        // formData.append('sha256', artifact.sha256);

        const req = new HttpRequest('POST', this.url + '/', formData, {
            reportProgress: true,
        });

        return this.http
            .request(req)
            .pipe(
                tap((newObject: CollectionUpload) =>
                    this.log(`Uploaded new ${this.serviceName}`),
                ),
            );
    }
}

@Injectable()
export class CollectionListService extends GenericQuery<CollectionList> {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/ui/collections',
            'collection',
        );
    }
}

@Injectable()
export class CollectionDetailService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/galaxyui/collection',
            'collection',
        );
    }

    get(namespace: string, name: string): Observable<CollectionDetail> {
        return this.http
            .get<CollectionDetail>(`${this.url}/${namespace}/${name}`)
            .pipe(
                tap(_ => this.log('fetched collection detail')),
                catchError(this.handleError('Get', {} as CollectionDetail)),
            );
    }
}
