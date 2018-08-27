import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { PagedResponse } from '../paged-response';
import { Survey } from './survey';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json',
    }),
};
@Injectable()
export class SurveyService {
    private url = '/api/v1/community_surveys';

    constructor(private http: HttpClient, private notificationService: NotificationService) {}

    query(params?: any): Observable<Survey[]> {
        params.page_size = 1000;
        return this.http.get<PagedResponse>(this.url + '/', { params: params }).pipe(
            map(response => response.results),
            tap(_ => this.log('fetched surveys')),
            catchError(this.handleError('Query', [] as Survey[])),
        );
    }

    save(survey: Survey): Observable<Survey> {
        let httpResult: Observable<Object>;
        if (survey.id) {
            httpResult = this.http.put<Survey>(`${this.url}/${survey.id}/`, survey, httpOptions);
        } else {
            httpResult = this.http.post<Survey>(`${this.url}/`, survey, httpOptions);
        }

        return httpResult.pipe(
            tap((newSurvey: Survey) => this.log(`Saved survey w/ id=${newSurvey.id}`)),
            catchError(this.handleError<Survey>('Save')),
        );
    }

    private handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(`${operation} survey error: ${error.message}`);
            this.notificationService.httpError(`${operation} survey failed:`, { data: error });

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    private log(message: string) {
        console.log('SurveyService: ' + message);
    }
}
