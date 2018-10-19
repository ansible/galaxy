import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { ApiRoot } from './api-root';

@Injectable()
export class ApiRootService {
    private url = '/api/';

    constructor(
        private http: HttpClient,
        private notificationService: NotificationService,
    ) {}

    get(): Observable<ApiRoot> {
        return this.http.get<ApiRoot>(this.url).pipe(
            tap(_ => this.log('fetched api information')),
            catchError(this.handleError<ApiRoot>(`get api root`)),
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
        console.log('ApiRootsService: ' + message);
    }
}
