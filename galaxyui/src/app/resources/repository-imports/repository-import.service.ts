import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { PagedResponse } from '../paged-response';
import { RepositoryImport } from './repository-import';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json',
    }),
};

@Injectable()
export class RepositoryImportService {
    private url = '/api/v1/imports';

    constructor(private http: HttpClient, private notificationService: NotificationService) {}

    query(params): Observable<RepositoryImport[]> {
        return this.http.get<PagedResponse>(this.url, { params: params }).pipe(
            map(response => response.results),
            tap(_ => this.log('fetched repository imports')),
            catchError(this.handleError('Query', [])),
        );
    }

    save(params: any): Observable<RepositoryImport> {
        return this.http.post<RepositoryImport>(`${this.url}/`, params, httpOptions).pipe(
            tap((newImport: RepositoryImport) => this.log(`Saved repository import`)),
            catchError(this.handleError<RepositoryImport>('Save')),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} repository import error: ${error.message}`);
            this.notificationService.httpError(`${operation} repository import failed:`, { data: error });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('RepositoryImportService: ' + message);
    }
}
