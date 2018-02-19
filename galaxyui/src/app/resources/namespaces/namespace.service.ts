import { Injectable }              from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';


import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Namespace } from './namespace';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service'
import { QueryResponse }       from "../query-response";


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

    query(): Observable<Namespace[]> {
        return this.http.get<QueryResponse>(this.url)
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched namespaces')),
                catchError(this.handleError('Query', []))
            );
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
            tap((namespace: Namespace) => this.log(`Saved namespace w/ id=${namespace.id}`)),
            catchError(this.handleError<Namespace>('Save'))
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
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} namespace error: ${error.message}`);
            this.notificationService.httpError(`${operation} namespace failed:`, {data: error});

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('NamespaceService: ' + message);
    }
}
