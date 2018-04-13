import { Injectable }              from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Platform }            from './platform';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service'
import { PagedResponse }       from "../paged-response";

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json'
    })
};

@Injectable()
export class PlatformService {

    private url = '/api/v1/platforms';
    private searchUrl = '/api/v1/search/platforms';

    constructor(private http: HttpClient,
                private notificationService: NotificationService) {
    }

    query(params?: any ): Observable<Platform[]> {
        return this.http.get<PagedResponse>(this.url + '/', {params: params})
            .pipe(
                map(response => response.results),
               tap(_ => this.log('fetched repositories')),
               catchError(this.handleError('Query', [] as Platform[]))
            );
    }

    search(params?: any ): Observable<Platform[]> {
        return this.http.get<PagedResponse>(this.searchUrl + '/', {params: params})
            .pipe(
                map(response => response.results),
               tap(_ => this.log('fetched repositories')),
               catchError(this.handleError('Query', [] as Platform[]))
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
        console.log('PlatformService: ' + message);
    }

}
