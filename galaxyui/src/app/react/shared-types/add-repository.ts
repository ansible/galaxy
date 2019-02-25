export class RepositorySource {
    name: string;
    description: string;
    stargazers_count: number;
    watchers_count: number;
    forks_count: number;
    open_issues_count: number;
    default_branch: string;
    related: any;
    summary_fields: any;
    isSelected: boolean;
}

export class ProviderNamespace {
    id: number;
    name: string;
    description: string;
    display_name: string;
    avatar_url: string;
    location: string;
    company: string;
    email: string;
    html_url: string;
    followers: number;
    provider: number;
    provider_name: string;
    related: object;
    summary_fields: any;
    repoSources: RepositorySource[];
    filteredSources: RepositorySource[];
}

export enum View {
    PickImport,
    RepoImport,
    CollectionImport,
}

export class ButtonConfig {
    back: boolean;
    okay: {
        enabled: boolean;
        text: string;
    };
    cancel: boolean;
}
