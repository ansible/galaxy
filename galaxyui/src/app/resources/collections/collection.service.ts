import { HttpClient, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng';
import { CollectionUpload } from './collection';

import { ServiceBase } from '../base/service-base';
import { Observable } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable()
export class CollectionUploadService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(http, notificationService, '/api/v1/collections', 'collection');
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
