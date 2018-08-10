import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Namespace } from './namespace';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';


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

    encounteredErrors = false;

    query(params?: any): Observable<Namespace[]> {
        return this.http.get<PagedResponse>(this.url + '/', { params: params })
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched namespaces')),
                catchError(this.handleError('Query', []))
            );
    }

    pagedQuery(params: any): Observable<PagedResponse> {
        if (params && typeof params === 'object') {
            return this.http.get<PagedResponse>(this.url + '/', { params: params })
                .pipe(
                    tap(_ => this.log('fetched paged content')),
                    catchError(this.handleError('Query', {} as PagedResponse))
                );
        }
        if (params && typeof params === 'string') {
            return this.http.get<PagedResponse>(this.url + '/' + params)
                .pipe(
                    tap(_ => this.log('fetched paged content')),
                    catchError(this.handleError('Query', {} as PagedResponse))
                );
        }
        return this.http.get<PagedResponse>(this.url + '/')
            .pipe(
                tap(_ => this.log('fetched paged content')),
                catchError(this.handleError('Query', {} as PagedResponse))
            );
    }

    get(id: number): Observable<Namespace> {
        const url = `${this.url}/${id}/`;
        return this.http.get<Namespace>(url).pipe(
            tap(_ => this.log(`fetched namespace id=${id}`)),
            catchError(this.handleError<Namespace>(`Get id=${id}`))
        );
    }

    save(namespace: Namespace): Observable<Namespace> {
        let httpResult: Observable<Object>;
        if (namespace.id) {
            httpResult = this.http.put<Namespace>(`${this.url}/${namespace.id}/`, namespace, httpOptions);
        } else {
            httpResult = this.http.post<Namespace>(`${this.url}/`, namespace, httpOptions);
        }
        return httpResult.pipe(
            tap((newNamespace: Namespace) => this.log(`Saved namespace w/ id=${newNamespace.id}`)),
            catchError(this.handleError<Namespace>('Save', namespace))
        );
    }

    delete (namespace: Namespace | number): Observable<any> {
        const id = typeof namespace === 'number' ? namespace : namespace.id;
        const url = `${this.url}/${id}`;

        return this.http.delete<any>(url, httpOptions).pipe(
            tap(_ => this.log(`deleted namespace id=${id}`)),
            catchError(this.handleError<any>('Delete'))
        );
    }

    private handleError<T>(operation = '', result?: T) {
        this.encounteredErrors = false;
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} namespace error: ${error.message}`);
            if (typeof error === 'object' && 'error' in error && typeof error['error'] === 'object' &&
                result !== undefined) {
                // Unpack error messages, sending each to the notification service
                for (const fld in error['error']) {
                    if (error['error'].hasOwnProperty(fld)) {
                        if (typeof error['error'][fld] !== 'object') {
                            const msg = result[fld];
                            this.notificationService.httpError(error['error'][fld], { data: { message: msg } });
                        } else {
                            for (const idx in error['error'][fld]) {
                                if (result[fld]) {
                                    if (Array.isArray(result[fld]) && idx < result[fld].length) {
                                        const msg = result[fld][idx]['name'];
                                        this.notificationService.httpError(error['error'][fld][idx], { data: { message: msg } });
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                // Nothing to unpack. Raise the raw error to the notification service.
                this.notificationService.httpError(`${operation} namespace failed:`, { data: error });
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
