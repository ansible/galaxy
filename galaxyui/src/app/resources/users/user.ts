export class User {
    id: number;
    username: string;
    active: boolean;
    email: string;
    staff: boolean;
    full_name: string;
    date_joined: string;
    avatar_url: string;
    github_user: string;
    url: string;
    cache_refreshed: boolean;
    summary_fields: any;
    related: any;
    selected: boolean;
    notify_survey: boolean;
    notify_import_fail: boolean;
    notify_import_success: boolean;
    notify_content_release: boolean;
    notify_author_release: boolean;
    notify_galaxy_announce: boolean;
    users_followed: any;
    repositories_followed: any;
}
