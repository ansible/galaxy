import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { catchError, map, tap } from 'rxjs/operators';

import { HttpClient } from '@angular/common/http';

import { Observable, of } from 'rxjs';

import { PagedResponse } from '../paged-response';

import { Content } from './content';

@Injectable()
export class ContentService {
    constructor(
        private http: HttpClient,
        private notificationService: NotificationService,
    ) {}

    private url = '/api/v1/content/';

    query(params?: any): Observable<Content[]> {
        return this.http.get<PagedResponse>(this.url, { params: params }).pipe(
            map(result => result.results as Content[]),
            tap(_ => this.log('fetched content')),
            catchError(this.handleError('Query', [] as Content[])),
        );
    }

    pagedQuery(params?: any): Observable<PagedResponse> {
        if (params && typeof params === 'object') {
            return this.http
                .get<PagedResponse>(this.url, { params: params })
                .pipe(
                    tap(_ => this.log('fetched paged content')),
                    catchError(this.handleError('Query', {} as PagedResponse)),
                );
        }
        if (params && typeof params === 'string') {
            return this.http.get<PagedResponse>(this.url + params).pipe(
                tap(_ => this.log('fetched paged content')),
                catchError(this.handleError('Query', {} as PagedResponse)),
            );
        }
        return this.http.get<PagedResponse>(this.url).pipe(
            tap(_ => this.log('fetched paged content')),
            catchError(this.handleError('Query', {} as PagedResponse)),
        );
    }

    get(id: number): Observable<Content> {
        return this.http.get<Content>(`${this.url}${id.toString()}/`).pipe(
            tap(_ => this.log('fetched content')),
            catchError(this.handleError('Get', {} as Content)),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} provider source error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {
                data: error,
            });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ContentService: ' + message);
    }
}
