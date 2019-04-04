export class CollectionUpload {
    id: number;
    file: File;
    sha256: string;
}

export class CollectionVersion {
    id: number;
    quality_score: number;
    version: string;
    metadata: {
        tags: string[];
        authors: string[];
        license: string;
        homepage: string;
        description: string;
    };
    contents: any;
    created: string;
    modified: string;
    readme: string;
}

class CollectionBase {
    id: number;
    name: string;
    description: string;
    download_count: number;
    deprecated: boolean;
    community_score: number;
    community_survey_count: number;
    latest_version: CollectionVersion;
}

export class CollectionList extends CollectionBase {
    namespace: number;
}

export class CollectionDetail extends CollectionBase {
    all_versions: CollectionVersion[];
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
