export class UserPreferences {
    preferences: {
        notify_survey: boolean;
        notify_import_fail: boolean;
        notify_import_success: boolean;
        notify_content_release: boolean;
        notify_author_release: boolean;
        notify_galaxy_announce: boolean;
        ui_notify_survey: boolean;
        ui_notify_import_fail: boolean;
        ui_notify_import_success: boolean;
        ui_notify_content_release: boolean;
        ui_notify_author_release: boolean;
        ui_notify_galaxy_announce: boolean;
    };

    namespaces_followed: number[];
    repositories_followed: number[];
    collections_followed: number[];
    summary_fields: any;
}
