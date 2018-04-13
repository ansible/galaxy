class Related {
    owner: string;
    notifications: string;
    repository: string;
    provider: string;
    namespace: string;
}

class Owner {
    username: string;
    id: number;
    full_name: string;
}

class Notification {
    id: number;
    travis_build_url: string;
    commit_message: string;
    committed_at: string;
    commit: string;
}

class TaskMessage {
    id: number;
    message_type: string;
    message_text: string;
}

class ProviderNamespace {
    id: number;
    name: string;
}

class Namespace {
    id: number;
    name: string;
}

class Repository {
    id: number;
    name: string;
    original_name: string;
    import_branch: string;
}

class SummaryFields {
    owner: Owner;
    notifications: Notification[];
    task_messages: TaskMessage[];
    provider_namespace: ProviderNamespace;
    namespace: Namespace;
    repository: Repository;
}

export class Import {
    url: string;
    related: Related;
    summary_fields: SummaryFields;
    id: number;
    owner: number;
    celery_task_id: number;
    state: string;
    started: string;
    finished: string;
    modified: string;
    created: string;
    active: boolean;
    import_branch;
    commit: string;
    commit_message: string;
    commit_url: string;
    travis_status_url: string;
    travis_build_url: string;
    last_run: string;
}
