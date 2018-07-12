import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable }              from '@angular/core';

import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse }       from '../paged-response';
import { Repository }          from './repository';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json'
    })
};

@Injectable()
export class RepositoryService {

    private url = '/api/v1/repositories';

    constructor(private http: HttpClient,
                private notificationService: NotificationService) {
    }

    query(params?: any): Observable<Repository[]> {
        return this.http.get<PagedResponse>(this.url + '/', {params: params})
            .pipe(
                map(response => response.results as Repository[]),
                tap(_ => this.log('fetched repositories')),
                catchError(this.handleError('Query', [] as Repository[]))
            );
    }

    pagedQuery(params?: any): Observable<PagedResponse> {
        if (params && typeof params === 'object') {
            return this.http.get<PagedResponse>(this.url + '/', {params: params})
                .pipe(
                    tap(_ => this.log('fetched repositories')),
                    catchError(this.handleError('Query', {} as PagedResponse))
                );
        }
        if (params && typeof params === 'string') {
            return this.http.get<PagedResponse>(this.url + '/' + params)
                .pipe(
                    tap(_ => this.log('fetched repositories')),
                    catchError(this.handleError('Query', {} as PagedResponse))
                );
        }
        return this.http.get<PagedResponse>(this.url + '/')
            .pipe(
                tap(_ => this.log('fetched repositories')),
                catchError(this.handleError('Query', {} as PagedResponse))
            );
    }

    get(id: number): Observable<Repository> {
        return this.http.get<Repository>(`${this.url}/${id.toString()}/`)
            .pipe(
                tap(_ => this.log('Fetched repository')),
                catchError(this.handleError('Get', {} as Repository))
            );
    }

    save(repository: Repository): Observable<Repository> {
        let httpResult: Observable<Object>;
        if (repository.id) {
            httpResult = this.http.put<Repository>(`${this.url}/${repository.id}/`, repository, httpOptions);
        } else {
            httpResult = this.http.post<Repository>(`${this.url}/`, repository, httpOptions);
        }

        return httpResult.pipe(
            tap((newRepo: Repository) => this.log(`Saved repository w/ id=${newRepo.id}`)),
            catchError(this.handleError<Repository>('Save'))
        );
    }

    destroy(repository: Repository): Observable<any> {
        return this.http.delete<any>(`${this.url}/${repository.id}/`)
            .pipe(
                tap(_ => this.log(`Deleted repository w/ id=${repository.id}`)),
                catchError(this.handleError<any>('Save'))
            );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            let data = error;
            if (error['error']) {
                // Check if API returned a field-level validation error
                const msg = error['error'];
                if (typeof msg === 'object') {
                    for (const key in msg) {
                        if (msg.hasOwnProperty(key)) {
                            data = {message: msg[key]};
                            break;
                        }
                    }
                }
            }
            this.log(`${operation} repository error: ${error.message}`);
            this.notificationService.httpError(`${operation} repository failed:`, {data: data});

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('RepositoryService: ' + message);
    }

}
