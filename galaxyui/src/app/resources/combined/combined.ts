import { CollectionList, CollectionDetail } from '../collections/collection';
import { Repository } from '../repositories/repository';
import { Namespace } from '../namespaces/namespace';
import { ContentFormat } from '../../enums/format';
import { CollectionImport } from '../imports/import';

export class Content {
    url: string;
    related: object;
    summary_fields: object;
    id: number;
    created: string;
    modified: string;
    name: string;
    role_type: string;
    namespace: number;
    is_valid: boolean;
    min_ansible_version: string;
    issue_tracker_url: string;
    license: string;
    company: string;
    description: string;
    travis_status_url: string;
    download_count: number;
    imported: string;
    relevance: number;
    search_rank: number;
    download_rank: number;
    active: boolean;
    open_issues_count: number;
    commit_url: string;
    github_user: string;
    forks_count: number;
    github_branch: string;
    github_repo: string;
    commit_message: string;
    commit: string;
    stargazers_count: number;
    namespace_name: string;
}

export class PaginatedRepoCollection {
    collection: {
        count: number;
        results: CollectionList[];
    };

    repository: {
        count: number;
        results: Repository[];
    };
}

export class PaginatedCombinedSearch {
    collection: {
        count: number;
        results: CollectionList[];
    };

    content: {
        count: number;
        results: Content[];
    };
}

export class RepoOrCollectionResponse {
    type: ContentFormat;
    data: {
        collection?: CollectionDetail;
        collection_import?: CollectionImport;
        content?: Content[];
        repository?: Repository;
        namespace?: Namespace;
    };
}
