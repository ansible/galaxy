import { HttpClient } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';

export class GenericQuery<ServiceType> {
    protected ObjectType: any;

    constructor(protected http: HttpClient, protected notificationService: NotificationService, protected url, protected serviceName) {}

    query(params?: any): Observable<ServiceType[]> {
        return this.http.get<PagedResponse>(this.url + '/', { params: params }).pipe(
            map(response => response.results),
            tap(_ => this.log(`fetched ${this.serviceName}`)),
            catchError(this.handleError('Query', [] as ServiceType[])),
        );
    }

    handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} ${this.serviceName} error: ${error.message}`);
            this.notificationService.httpError(`${operation} ${this.serviceName} failed:`, { data: error });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    log(message: string) {
        console.log(`${this.serviceName}: ${message}`);
    }
}
