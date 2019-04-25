import { CollectionList } from '../collections/collection';
import { Repository } from '../repositories/repository';

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
