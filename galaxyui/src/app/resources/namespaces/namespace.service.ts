import { Injectable }              from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';


import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Namespace } from './namespace';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service'
import { PagedResponse }       from "../paged-response";


const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json'
    })
};


@Injectable()
export class NamespaceService {
    private url = '/api/v1/namespaces';

    constructor(private http: HttpClient,
                private notificationService: NotificationService) {
    }

    encounteredErrors: boolean = false;

    query(): Observable<Namespace[]> {
        return this.http.get<Namespace[]>(this.url)
            .pipe(
                map(response => response),
                tap(_ => this.log('fetched namespaces')),
                catchError(this.handleError('Query', []))
            );
        //return this.http.get<PagedResponse>(this.url)
        //    .pipe(
        //        map(response => response.results),
        //        tap(_ => this.log('fetched namespaces')),
        //        catchError(this.handleError('Query', []))
        //    );
    }

    get(id: number): Observable<Namespace> {
        const url = `${this.url}/${id}`;
        return this.http.get<Namespace>(url).pipe(
            tap(_ => this.log(`fetched namespace id=${id}`)),
            catchError(this.handleError<Namespace>(`Get id=${id}`))
        );
    }

    save(namespace: Namespace): Observable<Namespace> {
        let httpResult: Observable<Object>;
        if (namespace.id) {
            httpResult = this.http.put<Namespace>(`${this.url}/${namespace.id}`, namespace, httpOptions);
        } else {
            httpResult = this.http.post<Namespace>(`${this.url}/`, namespace, httpOptions);
        }
        return httpResult.pipe(
            tap((newNamespace: Namespace) => this.log(`Saved namespace w/ id=${newNamespace.id}`)),
            catchError(this.handleError<Namespace>('Save', namespace))
        );
    }

    delete (namespace: Namespace | number): Observable<Namespace> {
        const id = typeof namespace === 'number' ? namespace : namespace.id;
        const url = `${this.url}/${id}`;

        return this.http.delete<Namespace>(url, httpOptions).pipe(
            tap(_ => this.log(`deleted namespace id=${id}`)),
            catchError(this.handleError<Namespace>('Delete'))
        );
    }

    private handleError<T>(operation = '', result?: T) {
        this.encounteredErrors = false;
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} namespace error: ${error.message}`);
            if ('error' in error && result !== undefined) {
                // Unpack error messages, sending each to the notification service
                for (var fld in error['error']) {
                    if (typeof error['error'][fld] != 'object') {
                        let msg = result[fld]
                        this.notificationService.httpError(error['error'][fld], {data: {message: msg}});
                    } else {
                        for (var idx in error['error'][fld]) {
                            if (result[fld]) {
                                if (Array.isArray(result[fld]) && idx < result[fld].length) {
                                    let msg = result[fld][idx]['name']
                                    this.notificationService.httpError(error['error'][fld][idx], {data: {message: msg}});
                                }
                            }
                        }
                    }
                }
            } else {
                // Nothing to unpack. Raise the raw error to the notification service.
                this.notificationService.httpError(`${operation} namespace failed:`, {data: error});
            }
            // Let the app keep running by returning an empty result.
            this.encounteredErrors = true;
            return of({} as T);
        };
    }

    private log(message: string) {
        console.log('NamespaceService: ' + message);
    }
}
