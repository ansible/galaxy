export class CollectionUpload {
    id: number;
    file: File;
    sha256: string;
}

class ContentSummary {
    total_count: number;
    contents: {
        module: string[];
        role: string[];
        plugin: string[];
    };
}

export class CollectionVersion {
    id: number;
    quality_score: number;
    version: string;
    download_url?: string;
    metadata: {
        tags: string[];
        authors: string[];
        license: string;
        description: string;
        homepage?: string;
        documentation?: string;
        issues?: string;
        repository?: string;
    };
    contents: any;
    content_summary?: ContentSummary;
    created: string;
    modified: string;
    readme_html: string;
}

export class CollectionList {
    id: number;
    name: string;
    description: string;
    download_count: number;
    deprecated: boolean;
    community_score: number;
    community_survey_count: number;
    latest_version: CollectionVersion;
    content_match?: ContentSummary;

    namespace: {
        id: number;
        description: string;
        active: boolean;
        name: string;
        avatar_url: string;
        location: string;
        company: string;
        email: string;
        html_url: string;
        is_vendor: boolean;
        owners: number[];
    };
}

export class CollectionDetail extends CollectionList {
    all_versions: CollectionVersion[];
}
