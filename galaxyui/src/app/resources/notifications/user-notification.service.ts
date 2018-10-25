import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';

import { UserNotification } from './user-notification';

import { GenericQuerySave } from '../base/generic-query-save';

@Injectable({
    providedIn: 'root',
})
export class UserNotificationService extends GenericQuerySave<
    UserNotification
> {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/me/notifications',
            'user-notification',
        );
    }

    getUnread(): Observable<any> {
        const url = this.url + '/unread/';
        return this.http.get<any>(url).pipe(
            tap(_ => this.log(`fetched unread ${this.serviceName}`)),
            catchError(this.handleError('Get', {} as any)),
        );
    }

    deleteAll(): Observable<any> {
        const url = this.url + '/clear/';
        return this.http.delete<any>(url, this.httpOptions).pipe(
            tap(_ => this.log('deleted notifications')),
            catchError(this.handleError('Delete', {} as any)),
        );
    }

    clearAll(): Observable<any> {
        const url = this.url + '/clear/';
        return this.http.put<any>(url, this.httpOptions).pipe(
            tap(_ => this.log('cleared unread notifications')),
            catchError(this.handleError('Put', {} as any)),
        );
    }
}
