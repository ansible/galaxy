export class CollectionUpload {
    id: number;
    file: File;
    sha256: string;
}

export class CollectionList {
    id: number;
    name: string;
    description: string;
    format: string;
    is_enabled: boolean;
    url: string;
    external_url: string;
    last_import: string;
    last_import_state: string;
    download_count: number;
    deprecated: boolean;
    community_score: number;
    quality_score: number;
    quality_score_date: string;
    community_survey_count: number;
    latest_version: {
        version: string;
        metadata: any;
        contents: any;
    };
}
