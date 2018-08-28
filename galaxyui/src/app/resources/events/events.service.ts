import { Injectable } from '@angular/core';

import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';
import { Event } from './event';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json',
    }),
};

@Injectable()
export class EventsService {
    private url = '/api/v1/events';

    constructor(private http: HttpClient, private notificationService: NotificationService) {}

    query(params?: any): Observable<Event[]> {
        return this.http.get<PagedResponse>(this.url + '/', { params: params }).pipe(
            map(response => response.results),
            tap(_ => this.log('fetched events')),
            catchError(this.handleError('Query', [] as Event[])),
        );
    }

    save(event: Event): Observable<Event> {
        let httpResult: Observable<Object>;
        if (event.id) {
            httpResult = this.http.put<Event>(`${this.url}/${event.id}/`, event, httpOptions);
        } else {
            httpResult = this.http.post<Event>(`${this.url}/`, event, httpOptions);
        }
        // Note we're not catching the error here. Letting it bubble up to the caller.
        return httpResult.pipe(tap((newEvent: Event) => this.log(`Saved event w/ id=${event.id}`)));
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} repository error: ${error.message}`);
            this.notificationService.httpError(`${operation} repository failed:`, { data: error });
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('EventService: ' + message);
    }
}
