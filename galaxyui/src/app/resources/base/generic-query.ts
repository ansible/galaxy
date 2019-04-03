import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';

import { ServiceBase } from './service-base';

export class GenericQuery<ServiceType> extends ServiceBase {
    protected ObjectType: any;

    constructor(
        http: HttpClient,
        notificationService: NotificationService,
        url,
        serviceName,
    ) {
        super(http, notificationService, url, serviceName);
    }

    query(params?: any, urlExtras?: string): Observable<ServiceType[]> {
        let objectUrl = this.url;

        if (urlExtras) {
            objectUrl = this.append_to_url(this.url, urlExtras);
        }

        let objectParams = null;
        if (params) {
            if (typeof params === 'string') {
                objectUrl += `/?${params}`;
            } else {
                objectParams = params;
            }
        }
        return this.http
            .get<PagedResponse>(objectUrl, { params: objectParams })
            .pipe(
                map(response => response.results),
                tap(_ => this.log(`fetched ${this.serviceName}`)),
                catchError(this.handleError('Query', [] as ServiceType[])),
            );
    }

    pagedQuery(params?: any, urlExtras?: string): Observable<PagedResponse> {
        let objectUrl = this.url;

        if (urlExtras) {
            objectUrl = this.append_to_url(this.url, urlExtras);
        }

        let objectParams = null;
        if (params) {
            if (typeof params === 'string') {
                objectUrl += `?${params}`;
            } else {
                objectParams = params;
            }
        }
        return this.http
            .get<PagedResponse>(objectUrl + '/', { params: objectParams })
            .pipe(
                tap(_ => this.log(`fetched ${this.serviceName}`)),
                catchError(this.handleError('Query', {} as PagedResponse)),
            );
    }

    get(id: number, urlExtras?: string): Observable<ServiceType> {
        let objectUrl = this.url;

        if (urlExtras) {
            objectUrl = this.append_to_url(this.url, urlExtras);
        }

        return this.http
            .get<ServiceType>(`${objectUrl}/${id.toString()}/`)
            .pipe(
                tap(_ => this.log(`fetched ${this.serviceName}`)),
                catchError(this.handleError('Get', {} as ServiceType)),
            );
    }
}
