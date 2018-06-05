import { Injectable }           from '@angular/core';
import { NotificationService }  from "patternfly-ng/notification/notification-service/notification.service";
import { catchError, map, tap } from "rxjs/operators";

import {
    HttpClient,
    HttpHeaders,
} from "@angular/common/http";

import { Observable }    from 'rxjs/Observable';
import { of }            from 'rxjs/observable/of';
import { PagedResponse } from '../paged-response';

import {
    Content,
    ContentResponse
} from './content';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json'
    })
};

@Injectable()
export class ContentSearchService {

    constructor(
        private http: HttpClient,
        private notificationService: NotificationService
    ) { }

    private url: string = '/api/v1/search/content/';

    query(query?: string): Observable<ContentResponse> {
        let requestUrl = this.url;
        if (query)
            requestUrl += `?${query}`;
        return this.http.get<ContentResponse>(requestUrl)
            .pipe(
                 tap(_ => this.log('fetched content')),
                 catchError(this.handleError('Query', {} as ContentResponse))
            );
    }

    get(id: number): Observable<any> {
        return this.http.get<any>(`${this.url}${id.toString()}/`)
            .pipe(
                tap(_ => this.log('fetched import')),
                catchError(this.handleError('Get', []))
            );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} provider source error: ${error.message}`);
            this.notificationService.httpError(`${operation} user failed:`, { data: error });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('ContentSearch: ' + message);
    }
}
