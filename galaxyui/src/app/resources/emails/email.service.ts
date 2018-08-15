import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { Email } from './email';

import { Observable } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { GenericQuerySave } from '../base/generic-query-save';

@Injectable()
export class EmailService extends GenericQuerySave<Email> {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(http, notificationService, '/api/v1/emails', 'email');
    }

    sendVerification(email: Email) {
        const url = `${this.url}/verification/`;
        let httpResult: Observable<Email>;

        httpResult = this.http.post<any>(url, { email_address: email.id }, this.httpOptions);

        return httpResult.pipe(catchError(this.handleError<any>('Verify')));
    }

    verifyEmail(token: string): Observable<any> {
        const url = `${this.url}/verification/${token}/`;
        return this.http.get<any>(url).pipe(
            tap(_ => this.log('verified email')),
            catchError(this.handleError('Get')),
        );
    }

    deleteEmail(email: Email): Observable<any> {
        return this.http.delete<any>(`${this.url}/${email.id}/`).pipe(catchError(this.handleError('Delete')));
    }
}
