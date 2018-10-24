import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';

import { UserNotification } from './user-notification';

import { GenericQuery } from '../base/generic-query';

@Injectable({
    providedIn: 'root',
})
export class UserNotificationService extends GenericQuery<UserNotification> {
    constructor(http: HttpClient, notificationService: NotificationService) {
        super(
            http,
            notificationService,
            '/api/internal/me/notifications',
            'user-notification',
        );
    }
}
