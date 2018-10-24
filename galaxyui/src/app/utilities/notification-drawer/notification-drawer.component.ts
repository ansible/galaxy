import { Component, OnInit } from '@angular/core';
import { UserNotificationService } from '../../resources/notifications/user-notification.service';
import { UserNotification } from './resources/notifications/user-notification';

import { Action } from 'patternfly-ng/action/action';
import { ActionConfig } from 'patternfly-ng/action/action-config';

@Component({
    selector: 'app-notification-drawer',
    templateUrl: './notification-drawer.component.html',
    styleUrls: ['./notification-drawer.component.less'],
})
export class NotificationDrawerComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'NotificationDrawerComponent';

    constructor(private userNotificationService: UserNotificationService) {}
    showNotifications = false;
    notificationList: any;

    ngOnInit() {
        this.notificationList = [{ notifications: [] }];
    }

    toggleNotifcations() {
        this.showNotifications = !this.showNotifications;
        this.userNotificationService
            // .query({ order_by: '-created' })
            .query({ order_by: '-created', page_size: 20 })
            .subscribe(result => {
                const list = [];
                const actionConfig = {
                    moreActions: [
                        {
                            id: 'collection',
                            title: 'Go to Collection',
                        },
                        {
                            id: 'author',
                            title: 'Go to Author',
                        },
                    ],
                };
                for (const notification of result) {
                    list.push({
                        message: notification.message,
                        type: notification.type,
                        isViewing: true,
                        timeStamp: notification.created,
                        moreActions: actionConfig,
                    });
                }
                this.notificationList[0].notifications = list;
            });
    }

    handleAction($event, index) {
        console.log($event);
        console.log(index);
    }
}
