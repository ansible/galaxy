import { Component, OnInit, ViewEncapsulation } from '@angular/core';

import { NotificationEvent } from 'patternfly-ng';
import { Notification } from 'patternfly-ng/notification/notification';
import { NotificationService } from 'patternfly-ng/notification/notification-service/notification.service';

@Component({
    encapsulation: ViewEncapsulation.None,
    selector: 'user-notifications',
    templateUrl: './user-notifications.component.html',
    styleUrls: ['./user-notifications.component.less'],
})
export class UserNotificationsComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'UserNotificationsComponent';

    showClose = true;
    notifications: Notification[];

    constructor(private notificationService: NotificationService) {}

    ngOnInit(): void {
        this.notifications = this.notificationService.getNotifications();
    }

    handleAction($event: NotificationEvent): void {
        // Get the Action we provided and output its name
        console.log($event.action);
    }

    handleClose($event: NotificationEvent): void {
        this.notificationService.remove($event.notification);
    }

    handleViewingChange($event: NotificationEvent): void {
        this.notificationService.setViewing($event.notification, $event.isViewing);
    }
}
