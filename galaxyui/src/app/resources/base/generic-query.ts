import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';

import { ServiceBase } from './service-base';

export class GenericQuery<ServiceType> extends ServiceBase {
    protected ObjectType: any;

    constructor(http: HttpClient, notificationService: NotificationService, url, serviceName) {
        super(http, notificationService, url, serviceName);
    }

    query(params?: any): Observable<ServiceType[]> {
        let objectUrl = this.url;
        let objectParams = null;
        if (params) {
            if (typeof params === 'string') {
                objectUrl += `?${params}`;
            } else {
                objectParams = params;
            }
        }
        return this.http.get<PagedResponse>(objectUrl + '/', { params: objectParams }).pipe(
            map(response => response.results),
            tap(_ => this.log(`fetched ${this.serviceName}`)),
            catchError(this.handleError('Query', [] as ServiceType[])),
        );
    }

    get(id: number): Observable<ServiceType> {
        return this.http.get<ServiceType>(`${this.url}/${id.toString()}/`).pipe(
            tap(_ => this.log(`fetched ${this.serviceName}`)),
            catchError(this.handleError('Get', {} as ServiceType)),
        );
    }
}
