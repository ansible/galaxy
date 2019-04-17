import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';
import { NotificationType } from 'patternfly-ng/notification/notification-type';

export class ServiceBase {
    protected ObjectType: any;

    constructor(
        protected http: HttpClient,
        protected notificationService: NotificationService,
        protected url?,
        protected serviceName?,
    ) {}

    httpOptions = {
        headers: new HttpHeaders({
            'Content-Type': 'application/json',
        }),
    };

    handleError<T>(operation = '', result?: T) {
        return (error: any): Observable<T> => {
            console.error(`${operation} failed, error:`, error);
            this.log(
                `${operation} ${this.serviceName} error: ${error.message}`,
            );
            const apiResponse = error.error;

            // If we are saving data, we expect the error message to have the following shape
            // {field_name: ['Message 1', 'Message 2']}
            // because this is the error format that Django Rest serializer return
            if (
                typeof apiResponse === 'object' &&
                Object.keys(apiResponse).length > 0
            ) {
                for (const field of Object.keys(apiResponse)) {
                    let errorMessage = '';
                    if (typeof apiResponse[field] === 'string') {
                        errorMessage = apiResponse[field];
                    } else {
                        errorMessage = apiResponse[field].join(' ');
                    }
                    this.notificationService.message(
                        NotificationType.DANGER,
                        field,
                        errorMessage,
                        false,
                        null,
                        null,
                    );
                }
            } else if (typeof apiResponse === 'string') {
                this.notificationService.httpError(
                    `${operation} ${this.serviceName} failed: ${apiResponse}`,
                    { data: error },
                );
            } else {
                this.notificationService.httpError(
                    `${operation} ${this.serviceName} failed:`,
                    { data: error },
                );
            }

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }

    log(message: string) {
        console.log(`${this.serviceName}: ${message}`);
    }
}
