export class UserNotification {
    id: number;
    repository: any;
    message: string;
    type: string;
    seen: boolean;
    created: string;
}

export class NotificationPagedResponse {
    count: number;
    cur_page: number;
    num_pages: number;
    next_link: string;
    previous_link: string;
    next: string;
    previous: string;
    results: UserNotification[];
    unseen_notifications: number;
}
