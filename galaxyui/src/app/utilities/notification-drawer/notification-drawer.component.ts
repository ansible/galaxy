import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { Router } from '@angular/router';

import { UserNotificationService } from '../../resources/notifications/user-notification.service';
import { UserNotification } from '../../resources/notifications/user-notification';

@Component({
    selector: 'app-notification-drawer',
    templateUrl: './notification-drawer.component.html',
    styleUrls: ['./notification-drawer.component.less'],
})
export class NotificationDrawerComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'NotificationDrawerComponent';

    constructor(
        private userNotificationService: UserNotificationService,
        private router: Router,
    ) {}
    showNotifications = false;
    notificationList: any;
    rawNotifictions: UserNotification[];

    unreadCount: number;

    @Output()
    emitUnread = new EventEmitter<number>();

    ngOnInit() {
        this.notificationList = [{ notifications: [] }];
        this.userNotificationService.getUnread().subscribe(response => {
            this.setUnreadCount(response.count);
        });
        this.userNotificationService
            .pagedQuery({ order_by: '-created' })
            // .query({ order_by: '-created', page_size: 20 })
            .subscribe(result => {
                console.log(result);
                this.rawNotifictions = result.results;
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
                        {
                            id: 'delete',
                            title: 'Remove Notification',
                        },
                    ],
                };
                for (const notification of this.rawNotifictions) {
                    list.push({
                        message: notification.message,
                        type: notification.type,
                        isViewing: notification.seen,
                        timeStamp: notification.created,
                        moreActions: notification.repository
                            ? actionConfig
                            : null,
                        repo: notification.repository,
                        id: notification.id,
                    });
                }
                this.notificationList[0].notifications = list;
            });
    }

    toggleNotifcations() {
        this.showNotifications = !this.showNotifications;
    }

    handleAction($event, notify) {
        const repo = notify.repo;
        if ($event.id === 'author') {
            this.router.navigate(['/', repo.namespace]);
        } else if ($event.id === 'collection') {
            this.router.navigate(['/', repo.namespace, repo.name]);
        }
    }

    markAsRead(notify) {
        notify.isViewing = true;
        const n = this.rawNotifictions.find(x => {
            return notify.id === x.id;
        });

        n.seen = true;
        this.userNotificationService.save(n).subscribe();
        this.setUnreadCount(this.unreadCount - 1);
    }

    markAllAsRead() {
        this.userNotificationService.clearAll().subscribe(response => {
            if (response) {
                this.setUnreadCount(0);
                for (const n of this.notificationList[0].notifications) {
                    n.isViewing = true;
                }
            }
        });
    }

    deleteAll() {
        this.userNotificationService.deleteAll().subscribe(response => {
            if (response) {
                this.setUnreadCount(0);
            }
        });

        this.rawNotifictions = [];
        this.notificationList = [{ notifications: [] }];
    }

    close($event: boolean): void {
        this.showNotifications = false;
    }

    private setUnreadCount(count) {
        this.unreadCount = count;
        this.emitUnread.emit(this.unreadCount);
    }
}
