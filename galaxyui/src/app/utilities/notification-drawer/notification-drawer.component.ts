import {
    Component,
    OnInit,
    EventEmitter,
    Output,
    OnDestroy,
} from '@angular/core';
import { Router } from '@angular/router';

import { UserNotificationService } from '../../resources/notifications/user-notification.service';
import { UserNotification } from '../../resources/notifications/user-notification';

import { EmptyStateConfig } from 'patternfly-ng';
import { ActionConfig } from 'patternfly-ng';

import { interval } from 'rxjs';

@Component({
    selector: 'app-notification-drawer',
    templateUrl: './notification-drawer.component.html',
    styleUrls: ['./notification-drawer.component.less'],
})
export class NotificationDrawerComponent implements OnInit, OnDestroy {
    // Used to track which component is being loaded
    componentName = 'NotificationDrawerComponent';

    constructor(
        private userNotificationService: UserNotificationService,
        private router: Router,
    ) {}
    showNotifications = false;
    notificationList: any;
    rawNotifictions: UserNotification[] = [];
    emptyStateConfig: EmptyStateConfig;
    emptyActions: ActionConfig;
    polling = null;

    unreadCount: number;
    totalNotifications: number;
    loadedNotifications: number;
    notificationsToDisplay = 10;
    page = 1;

    @Output()
    emitUnread = new EventEmitter<number>();

    ngOnInit() {
        this.emptyStateConfig = {
            iconStyleClass: 'pficon-info',
            title:
                'No notifications. Visit preferences to configure your ' +
                'notification settings.',
        };

        this.notificationList = [
            { notifications: [], emptyStateConfig: this.emptyStateConfig },
        ];
        this.getNotifications();

        this.polling = interval(60 * 1000).subscribe(_ => {
            this.reloadNotifications();
        });
    }

    ngOnDestroy() {
        if (this.polling) {
            this.polling.unsubscribe();
        }
    }

    toggleNotifcations() {
        this.showNotifications = !this.showNotifications;

        // Render notifications if the drawer is being opened up.
        if (this.showNotifications) {
            this.prepNotifications();
        }
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
                this.rawNotifictions = [];
                this.notificationList = [{ notifications: [] }];

                this.loadedNotifications = 0;
                this.totalNotifications = 0;
            }
        });
    }

    close($event: boolean) {
        this.showNotifications = false;
    }

    loadMore() {
        if (this.totalNotifications <= this.loadedNotifications) {
            return;
        }

        this.page += 1;
        this.getNotifications(true);
    }

    private reloadNotifications() {
        if (!this.showNotifications) {
            this.page = 1;
            this.notificationsToDisplay = 10;
            this.rawNotifictions = [];
            this.notificationList[0].notifications = [];

            this.getNotifications();
        }
    }

    private setUnreadCount(count) {
        this.unreadCount = count;
        this.emitUnread.emit(this.unreadCount);
    }

    // Loads the raw data from the API into the component
    private getNotifications(prepDisplay = false) {
        this.notificationList[0].loading = true;
        this.userNotificationService
            // .pagedQuery({ order_by: '-created' })
            .pagedQuery({
                order_by: '-created',
                page_size: this.notificationsToDisplay,
                page: this.page,
            })
            .subscribe(result => {
                this.rawNotifictions = this.rawNotifictions.concat(
                    result.results,
                );

                this.totalNotifications = result.count;
                this.loadedNotifications = this.rawNotifictions.length;
                this.setUnreadCount(result.unseen_notifications);

                // If the drawer is opened when getNotifications is called,
                // the data needs to be rendered immediately so that the user
                // sees it.
                if (prepDisplay) {
                    this.prepNotifications();
                }
            });
    }

    // Renders the raw API data to be displayed. Data is only rendered when the
    // notification drawer is opened for performance reasons.
    private prepNotifications() {
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
        } as ActionConfig;
        for (const notification of this.rawNotifictions) {
            list.push({
                message: notification.message,
                type: notification.type,
                isViewing: notification.seen,
                timeStamp: notification.created,
                moreActions: notification.repository ? actionConfig : null,
                repo: notification.repository,
                id: notification.id,
            });
        }
        this.notificationList[0].notifications = list;

        this.notificationList[0].loading = false;
    }
}
