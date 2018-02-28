import { Injectable }              from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable }           from 'rxjs/Observable';
import { of }                   from 'rxjs/observable/of';
import { catchError, map, tap } from 'rxjs/operators';

import { Repository }          from './repository';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service'
import { QueryResponse }       from "../query-response";

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

    query(): Observable<Repository[]> {
        return this.http.get<QueryResponse>(this.url)
            .pipe(
                map(response => response.results),
                tap(_ => this.log('fetched repositories')),
                catchError(this.handleError('Query', []))
            );
    }

    save(repository: Repository): Observable<Repository> {
        let httpResult: Observable<Object>;
        if (repository.id) {
            httpResult = this.http.put<Repository>(`${this.url}/${repository.id}`, repository, httpOptions);
        } else {
            httpResult = this.http.post<Repository>(`${this.url}/`, repository, httpOptions);
        }

        return httpResult.pipe(
            tap((newRepo: Repository) => this.log(`Saved repository w/ id=${newRepo.id}`)),
            catchError(this.handleError<Repository>('Save'))
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
        console.log('RepositoryService: ' + message);
    }

}
