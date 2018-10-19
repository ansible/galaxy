import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { PagedResponse } from '../paged-response';
import { ContentBlock } from './content-block';

@Injectable()
export class ContentBlocksService {
    private url = '/api/v1/content_blocks/';

    constructor(
        private http: HttpClient,
        private notificationService: NotificationService,
    ) {}

    query(): Observable<ContentBlock[]> {
        return this.http.get<PagedResponse>(this.url).pipe(
            map(response => response.results as ContentBlock[]),
            tap(_ => this.log('fetched content blocks')),
            catchError(this.handleError<ContentBlock[]>('Query', [])),
        );
    }

    get(name: string): Observable<ContentBlock> {
        const url = `${this.url}${name}/`;
        return this.http.get<ContentBlock>(url).pipe(
            tap(_ => this.log('fetched content block')),
            catchError(
                this.handleError<ContentBlock>(`Get content block ${name}`),
            ),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} user error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, {
                data: error,
            });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ContentBlocksService: ' + message);
    }
}
