import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';

import { ServiceBase } from '../base/service-base';
import { UserPreferences } from './user-preferences';

@Injectable({
    providedIn: 'root',
})
export class PreferencesService extends ServiceBase {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(http, notificationService, '/api/internal/preferences', 'preferences');
    }

    preferences: UserPreferences = null;

    get(): Observable<UserPreferences> {
        if (this.preferences) {
            return of(this.preferences);
        }
        return this.http.get<UserPreferences>(`${this.url}/`).pipe(
            tap(_ => this.log(`fetched ${this.serviceName}`)),
            catchError(this.handleError('Get', {} as UserPreferences)),
            map(result => {
                this.preferences = result;
                return result;
            }),
        );
    }

    save(preferences: UserPreferences) {
        let httpResult: Observable<UserPreferences>;
        httpResult = this.http.put<UserPreferences>(`${this.url}/`, preferences, this.httpOptions);

        return httpResult.pipe(
            tap(_ => this.log(`Saved ${this.serviceName}`)),
            catchError(this.handleError<UserPreferences>('Save')),
            map(result => {
                if (result) {
                    this.preferences = result;
                    return result;
                }
            }),
        );
    }
}
