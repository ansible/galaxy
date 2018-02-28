export class RepositoryImport {
    id: number;
    github_user: string;
    github_repo: string;
    repository: number;
    owner: number;
    celery_task_id: number;
    state: string;
    started: string;
    finished: string;
    modified: string;
    created: string;
    active: boolean;
    commit: string;
    commit_message: string;
    commit_url: string;
    travis_status_url: string;
    travis_build_url: string;
    summary_fields: any;
    related: any;
}
