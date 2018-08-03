import { Injectable }              from '@angular/core';

import {
    HttpClient
} from '@angular/common/http';

import { NotificationService }  from 'patternfly-ng/notification/notification-service/notification.service';
import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { PagedResponse }        from '../paged-response';
import { Tag }                  from './tag';

@Injectable()
export class TagsService {

    private url = '/api/v1/tags';
    private searchUrl = '/api/v1/search/tags';

    constructor(private http: HttpClient,
                private notificationService: NotificationService) {
    }

    query(params?: any): Observable<Tag[]> {
        return this.http.get<PagedResponse>(this.url + '/', {params: params})
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched content types')),
                catchError(this.handleError('Query', [] as Tag[]))
            );
    }

    search(params?: any): Observable<Tag[]> {
        return this.http.get<PagedResponse>(this.searchUrl + '/', {params: params})
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched content types')),
                catchError(this.handleError('Query', [] as Tag[]))
            );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} repository error: ${error.message}`);
            this.notificationService.httpError(`${operation} repository failed:`, {data: error});

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('TagsService: ' + message);
    }
}
