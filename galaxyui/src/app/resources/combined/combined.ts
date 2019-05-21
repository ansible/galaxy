import { CollectionList, CollectionDetail } from '../collections/collection';
import { Repository } from '../repositories/repository';
import { Content } from '../content/content';
import { Namespace } from '../namespaces/namespace';
import { ContentFormat } from '../../enums/format';

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

export class RepoOrCollectionResponse {
    type: ContentFormat;
    data: {
        collection: CollectionDetail;
        content: Content[];
        repository: Repository;
        namespace: Namespace;
    };
}
