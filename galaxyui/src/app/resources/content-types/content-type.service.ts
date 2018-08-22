import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';
import { ContentType } from './content-type';

@Injectable()
export class ContentTypeService {
    private url = '/api/v1/content_types';

    constructor(private http: HttpClient, private notificationService: NotificationService) {}

    query(params?: any): Observable<ContentType[]> {
        return this.http.get<PagedResponse>(this.url + '/', { params: params }).pipe(
            map(response => response.results),
            tap(_ => this.log('fetched content types')),
            catchError(this.handleError('Query', [] as ContentType[])),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} repository error: ${error.message}`);
            this.notificationService.httpError(`${operation} repository failed:`, { data: error });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ContentTypeService: ' + message);
    }
}
